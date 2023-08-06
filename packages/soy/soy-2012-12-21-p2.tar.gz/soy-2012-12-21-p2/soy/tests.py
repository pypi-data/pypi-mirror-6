import unittest

import soy.utils
from soy.data import (
    SanitizedHtml,
    SanitizedHtmlAttribute,
    SanitizedJsStrChars,
    SanitizedJs,
    SanitizedUri,
    SanitizedCss,
    UnsanitizedText,
)


ASCII_CHARS = u"".join(unichr(i) for i in range(128))

# Substrings that might change the parsing mode of scripts they are embedded in.
EMBEDDING_HAZARDS = ["</script", "</style", "<!--", "-->", "<![CDATA[", "]]>"]


class TestStripHtmlTags(unittest.TestCase):

    def testEscapeHtml(self):
        escapedAscii = (
            u"&#0;\u0001\u0002\u0003\u0004\u0005\u0006\u0007\b\t\n\u000b\f\r\u000e\u000f" +
            u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017" +
            u"\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f" +
            u" !&quot;#$%&amp;&#39;()*+,-./" +
            u"0123456789:;&lt;=&gt;?" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[\\]^_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz{|}~\u007f")
        self.assertEquals(escapedAscii, soy.utils.escapeHtml(ASCII_CHARS))
        self.assertEquals(escapedAscii, soy.utils.escapeHtmlRcdata(ASCII_CHARS))
        self.assertEquals(escapedAscii, soy.utils.escapeHtmlAttribute(ASCII_CHARS))
        self.assertEquals(ASCII_CHARS, soy.utils.escapeHtml(SanitizedHtml(ASCII_CHARS)))

    def testEscapeHtmlRcdataSanitized(self):
        escapedAscii = (
            u"&#0;\u0001\u0002\u0003\u0004\u0005\u0006\u0007\b\t\n\u000b\f\r\u000e\u000f" +
            u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017" +
            u"\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f" +
            u" !&quot;#$%&&#39;()*+,-./" +
            u"0123456789:;&lt;=&gt;?" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[\\]^_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz{|}~\u007f")
        self.assertEquals(escapedAscii, soy.utils.escapeHtmlRcdata(SanitizedHtml(ASCII_CHARS)))

    def testEscapeHtmlAttributeNospace(self):
        # The minimal escapes.
        # Do not remove anything from this set without talking to your friendly local security-team@.
        self.assertEquals(
            u"&#9;&#10;&#11;&#12;&#13;&#32;&quot;&#39;&#96;&lt;&gt;&amp;",
            soy.utils.escapeHtmlAttributeNospace(u"\u0009\n\u000B\u000C\r \"'\u0060<>&"));

        escapedAscii = (
            u"&#0;\u0001\u0002\u0003\u0004\u0005\u0006\u0007\b&#9;&#10;&#11;&#12;&#13;\u000e\u000f" +
            u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017" +
            u"\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f" +
            u"&#32;!&quot;#$%&amp;&#39;()*+,&#45;.&#47;" +
            u"0123456789:;&lt;&#61;&gt;?" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[\\]^_" +
            u"&#96;abcdefghijklmno" +
            u"pqrstuvwxyz{|}~\u007f")
        self.assertEquals(escapedAscii, soy.utils.escapeHtmlAttributeNospace(ASCII_CHARS))

    def testFilterHtmlAttributes(self):
        self.assertEquals(u"dir", soy.utils.filterHtmlAttributes(u"dir"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlAttributes(u"><script>alert('foo')</script"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlAttributes(u"style"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlAttributes(u"onclick"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlAttributes(u"href"))

        self.assertEquals(
            u"a=1 b=2 dir=\"ltr\"",
            soy.utils.filterHtmlAttributes(SanitizedHtmlAttribute(u"a=1 b=2 dir=\"ltr\"")))
        # Should append a space to parse correctly
        self.assertEquals(
            u"foo=\"bar\" dir=ltr ",
            soy.utils.filterHtmlAttributes(SanitizedHtmlAttribute(u"foo=\"bar\" dir=ltr")))
        # Should append a space to parse correctly
        self.assertEquals(
            u"foo=\"bar\" checked ",
            soy.utils.filterHtmlAttributes(SanitizedHtmlAttribute(u"foo=\"bar\" checked")))
        # No duplicate space should be added"
        self.assertEquals(
            "foo=\"bar\" checked ",
            soy.utils.filterHtmlAttributes(SanitizedHtmlAttribute(u"foo=\"bar\" checked ")))

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.filterHtmlAttributes(hazard))

    def testFilterHtmlElementName(self):
        self.assertEquals(u"h1", soy.utils.filterHtmlElementName(u"h1"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlElementName(u"script"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlElementName(u"style"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlElementName(u"SCRIPT"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlElementName(u"><script>alert('foo')</script"))
        self.assertEquals(u"zSoyz", soy.utils.filterHtmlElementName(u"<h1>"))

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.filterHtmlElementName(hazard))

    def testEscapeJsString(self):
        # The minimal escapes.
        # Do not remove anything from this set without talking to your friendly local security-team@.
        self.assertEquals(
            u"\\x00 \\x22 \\x27 \\\\ \\r \\n \\u2028 \\u2029",
            soy.utils.escapeJsString(u"\u0000 \" \' \\ \r \n \u2028 \u2029"))

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.escapeJsString(hazard))

        # Check correctness of other Latins.
        escapedAscii = (
            u"\\x00\u0001\u0002\u0003\u0004\u0005\u0006\u0007\\x08\\t\\n\\x0b\\f\\r\u000e\u000f" +
            u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017" +
            u"\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f" +
            u" !\\x22#$%\\x26\\x27()*+,-.\\/" +
            u"0123456789:;\\x3c\\x3d\\x3e?" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[\\\\]^_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz{|}~\u007f");
        self.assertEquals(escapedAscii, soy.utils.escapeJsString(ASCII_CHARS))
        self.assertEquals(ASCII_CHARS, soy.utils.escapeJsString(SanitizedJsStrChars(ASCII_CHARS)))

    def testEscapeJsValue(self):
        self.assertEquals(  # Adds quotes.
            u"'Don\\x27t run with \\x22scissors\\x22.\\n'",
            soy.utils.escapeJsValue(u"Don't run with \"scissors\".\n"))
        self.assertEquals(
            u" 4 ",
            soy.utils.escapeJsValue(4))
        self.assertEquals(
            u" 4.5 ",
            soy.utils.escapeJsValue(4.5))
        self.assertEquals(
            u" true ",
            soy.utils.escapeJsValue(True));
        self.assertEquals(
            u" null ",
            soy.utils.escapeJsValue(None));
        self.assertEquals(
            u"foo() + bar",
            soy.utils.escapeJsValue(SanitizedJs(u"foo() + bar")))
        # Wrong content kind should be wrapped in a string.
        self.assertEquals(
            u"'foo() + bar'",
            soy.utils.escapeJsValue(SanitizedHtml(u"foo() + bar")))

    def testEscapeJsRegex(self):
        # The minimal escapes.
        # Do not remove anything from this set without talking to your friendly local security-team@.
        self.assertEquals(
            u"\\x00 \\x22 \\x27 \\\\ \\/ \\r \\n \\u2028 \\u2029" +
            #  RegExp operators.
            " \\x24\\x5e\\x2a\\x28\\x29\\x2d\\x2b\\x7b\\x7d\\x5b\\x5d\\x7c\\x3f",
            soy.utils.escapeJsRegex(
                u"\u0000 \" \' \\ / \r \n \u2028 \u2029" +
                u" $^*()-+{}[]|?"))

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.escapeJsRegex(hazard))

        escapedAscii = (
            u"\\x00\u0001\u0002\u0003\u0004\u0005\u0006\u0007\\x08\\t\\n\\x0b\\f\\r\u000e\u000f" +
            u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017" +
            u"\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f" +
            u" !\\x22#\\x24%\\x26\\x27\\x28\\x29\\x2a\\x2b\\x2c\\x2d\\x2e\\/" +
            u"0123456789\\x3a;\\x3c\\x3d\\x3e\\x3f" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ\\x5b\\\\\\x5d\\x5e_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz\\x7b\\x7c\\x7d~\u007f")
        self.assertEquals(escapedAscii, soy.utils.escapeJsRegex(ASCII_CHARS))

    def testEscapeUri(self):
        # The minimal escapes.
        # Do not remove anything from this set without talking to your friendly local security-team@.
        self.assertEquals(
            u"%00%0A%0C%0D%22%23%26%27%2F%3A%3D%3F%40",
            soy.utils.escapeUri(u"\u0000\n\f\r\"#&'/:=?@"));

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.escapeUri(hazard))

        escapedAscii = (
            u"%00%01%02%03%04%05%06%07%08%09%0A%0B%0C%0D%0E%0F" +
            u"%10%11%12%13%14%15%16%17%18%19%1A%1B%1C%1D%1E%1F" +
            u"%20%21%22%23%24%25%26%27%28%29%2A%2B%2C-.%2F" +
            u"0123456789%3A%3B%3C%3D%3E%3F" +
            u"%40ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ%5B%5C%5D%5E_" +
            u"%60abcdefghijklmno" +
            u"pqrstuvwxyz%7B%7C%7D~%7F")
        self.assertEquals(escapedAscii, soy.utils.escapeUri(ASCII_CHARS))
        # Test full-width.  The two characters at the right are a full-width '#' and ':'.
        # TODO JS and Java use different escaping
        #self.assertEquals(u"%EF%BC%83%EF%BC%9A", soy.utils.escapeUri(u"\uff03\uff1a"));
        # Test other unicode codepoints.
        # TODO JS and Java use different escaping
        #self.assertEquals(u"%C2%85%E2%80%A8", soy.utils.escapeUri(u"\u0085\u2028"));
        # Test Sanitized Content of the right kind. Note that some characters are still normalized --
        # specifically, ones that are allowed in URI's but not attributes but don't change meaning
        # (and parentheses since they're technically reserved).
        self.assertEquals(u"foo%28%27&%27%29", soy.utils.escapeUri(
            SanitizedUri(u"foo(%27&')")))
        # Test SanitizedContent of the wrong kind -- it should be completely escaped.
        self.assertEquals(u"%2528%2529", soy.utils.escapeUri(
            SanitizedHtml(u"%28%29")))

    def testNormalizeUri(self):
        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.normalizeUri(hazard))

        escapedAscii = (
            u"%00%01%02%03%04%05%06%07%08%09%0A%0B%0C%0D%0E%0F" +
            u"%10%11%12%13%14%15%16%17%18%19%1A%1B%1C%1D%1E%1F" +
            u"%20!%22#$%&%27%28%29*+,-./" +
            u"0123456789:;%3C=%3E?" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[%5C]^_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz%7B|%7D~%7F")
        self.assertEquals(escapedAscii, soy.utils.normalizeUri(ASCII_CHARS))

        # Test full-width.  The two characters at the right are a full-width '#' and ':'.
        escapedFullWidth = u"%EF%BC%83%EF%BC%9A"
        fullWidth = u"\uff03\uff1a"
        self.assertEquals(escapedFullWidth, soy.utils.normalizeUri(fullWidth))

    def testFilterNormalizeUri(self):
        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.filterNormalizeUri(hazard))

        escapedAscii = (
            u"%00%01%02%03%04%05%06%07%08%09%0A%0B%0C%0D%0E%0F" +
            u"%10%11%12%13%14%15%16%17%18%19%1A%1B%1C%1D%1E%1F" +
            u"%20!%22#$%&%27%28%29*+,-./" +
            u"0123456789:;%3C=%3E?" +
            u"@ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[%5C]^_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz%7B|%7D~%7F")
        self.assertEquals("#" + escapedAscii, soy.utils.filterNormalizeUri("#" + ASCII_CHARS))

        # Test full-width.  The two characters at the right are a full-width '#' and ':'.
        escapedFullWidth = u"%EF%BC%83%EF%BC%9A"
        fullWidth = u"\uff03\uff1a"
        self.assertEquals(escapedFullWidth, soy.utils.filterNormalizeUri(fullWidth))

        # Test filtering of URI starts.
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"javascript:"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"javascript:alert(1337)"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"vbscript:alert(1337)"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"livescript:alert(1337)"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"data:,alert(1337)"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"data:text/javascript,alert%281337%29"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"file:///etc/passwd"))
        self.assertNotIn(u"javascript\uff1a",
            soy.utils.filterNormalizeUri(u"javascript\uff1aalert(1337);"))

        # Testcases from http://ha.ckers.org/xss.html
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"JaVaScRiPt:alert(1337)"))
        self.assertEquals(
            u"#zSoyz",
            soy.utils.filterNormalizeUri(
                # Using HTML entities to obfuscate javascript:alert('XSS')
                u"&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;" +
                u"&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;"))
        self.assertEquals(
            u"#zSoyz",
            soy.utils.filterNormalizeUri(  # Using longer HTML entities to obfuscate the same.
                u"&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105" +
                u"&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116" +
                u"&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041"))
        self.assertEquals(
            u"#zSoyz",
            soy.utils.filterNormalizeUri(  # Using hex HTML entities to obfuscate the same.
                u"&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74" +
                u"&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"jav\tascript:alert('XSS');"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"jav&#x09;ascript:alert('XSS');"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"jav&#x0A;ascript:alert('XSS');"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"jav&#x0D;ascript:alert('XSS');"))
        self.assertEquals(
            u"#zSoyz",
            soy.utils.filterNormalizeUri(
                u"\nj\n\na\nv\na\ns\nc\nr\ni\np\nt\n:\na\nl\ne\nr\nt\n(\n1\n3\n3\n7\n)"))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(u"\u000e  javascript:alert('XSS');"))

        # Things we should accept.
        self.assertEquals(u"http://google.com/", soy.utils.filterNormalizeUri(u"http://google.com/"))
        self.assertEquals(u"https://google.com/", soy.utils.filterNormalizeUri(u"https://google.com/"))
        self.assertEquals(u"HTTP://google.com/", soy.utils.filterNormalizeUri(u"HTTP://google.com/"))
        self.assertEquals(u"?a=b&c=d", soy.utils.filterNormalizeUri(u"?a=b&c=d"))
        self.assertEquals(u"?a=b:c&d=e", soy.utils.filterNormalizeUri(u"?a=b:c&d=e"))
        self.assertEquals(u"//foo.com:80/", soy.utils.filterNormalizeUri(u"//foo.com:80/"))
        self.assertEquals(u"//foo.com/", soy.utils.filterNormalizeUri(u"//foo.com/"))
        self.assertEquals(u"/foo:bar/", soy.utils.filterNormalizeUri(u"/foo:bar/"))
        self.assertEquals(u"#a:b", soy.utils.filterNormalizeUri(u"#a:b"))
        self.assertEquals(u"#", soy.utils.filterNormalizeUri(u"#"))
        self.assertEquals(u"/", soy.utils.filterNormalizeUri(u"/"))
        self.assertEquals(u"", soy.utils.filterNormalizeUri(u""))
        self.assertEquals(u"javascript:handleClick%28%29", soy.utils.filterNormalizeUri(
            SanitizedUri(u"javascript:handleClick()")))
        self.assertEquals(u"#zSoyz", soy.utils.filterNormalizeUri(
            SanitizedHtml(u"javascript:handleClick()")))

    def testEscapeCssString(self):
        # The minimal escapes.
        # Do not remove anything from this set without talking to your friendly local security-team@.
        self.assertEquals(
            u"\\0  \\22  \\27  \\5c  \\a  \\c  \\d ",
            soy.utils.escapeCssString(u"\u0000 \" \' \\ \n \u000c \r"))

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.escapeCssString(hazard))

        escapedAscii = (
            u"\\0 \u0001\u0002\u0003\u0004\u0005\u0006\u0007\\8 \\9 \\a \\b \\c \\d \u000e\u000f" +
            u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017" +
            u"\u0018\u0019\u001A\u001B\u001C\u001D\u001E\u001F" +
            u" !\\22 #$%\\26 \\27 \\28 \\29 \\2a +,-.\\2f " +
            u"0123456789\\3a \\3b \\3c \\3d \\3e ?" +
            u"\\40 ABCDEFGHIJKLMNO" +
            u"PQRSTUVWXYZ[\\5c ]^_" +
            u"`abcdefghijklmno" +
            u"pqrstuvwxyz\\7b |\\7d ~\u007f")
        self.assertEquals(escapedAscii, soy.utils.escapeCssString(ASCII_CHARS))

    def testFilterCssValue(self):
        self.assertEquals(u"33px", soy.utils.filterCssValue(u"33px"))
        self.assertEquals(u"-.5em", soy.utils.filterCssValue(u"-.5em"))
        self.assertEquals(u"inherit", soy.utils.filterCssValue(u"inherit"))
        self.assertEquals(u"display", soy.utils.filterCssValue(u"display"))
        self.assertEquals(u"none", soy.utils.filterCssValue(u"none"))
        self.assertEquals(u"#id", soy.utils.filterCssValue(u"#id"))
        self.assertEquals(u".class", soy.utils.filterCssValue(u".class"))
        self.assertEquals(u"red", soy.utils.filterCssValue(u"red"))
        self.assertEquals(u"#aabbcc", soy.utils.filterCssValue(u"#aabbcc"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"expression"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"Expression"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"\\65xpression"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"\\65 xpression"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"-moz-binding"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"</style><script>alert('foo')</script>/*"))
        self.assertEquals(u"zSoyz", soy.utils.filterCssValue(u"color:expression('whatever')"))
        self.assertEquals(u"color:expression('whatever')", soy.utils.filterCssValue(
            SanitizedCss("color:expression('whatever')")))

        for hazard in EMBEDDING_HAZARDS:
            self.assertNotIn(hazard, soy.utils.filterCssValue(hazard))

    def testFilterNoAutoescape(self):
        # Filter out anything marked with sanitized content of kind "text" which indicates it
        # previously was constructed without any escaping.
        self.assertEquals(u"zSoyz", soy.utils.filterNoAutoescape(
            UnsanitizedText(u"x")))
        self.assertEquals(u"zSoyz", soy.utils.filterNoAutoescape(
            UnsanitizedText(u"<!@*!@(*!@(>")))

        # Everything else should be let through. Hope it's safe!
        self.assertEquals(u"<div>test</div>", soy.utils.filterNoAutoescape(
            SanitizedHtml(u"<div>test</div>")))
        self.assertEquals(u"foo='bar'", soy.utils.filterNoAutoescape(
            SanitizedHtmlAttribute(u"foo='bar'")))
        self.assertEquals(u".foo{color:green}", soy.utils.filterNoAutoescape(
            SanitizedCss(u".foo{color:green}")))
        self.assertEquals(u"<div>test</div>", soy.utils.filterNoAutoescape(u"<div>test</div>"))
        self.assertEquals(u"123", soy.utils.filterNoAutoescape(123))

    def stripHtmlTags(self, value):
        return soy.utils.stripHtmlTags(value)

    def testStripHtmlTags(self):
        self.assertEquals("", self.stripHtmlTags(""))
        self.assertEquals("Hello, World!", self.stripHtmlTags("Hello, World!"))
        self.assertEquals("Hello, World!", self.stripHtmlTags("<b>Hello, World!</b>"))
        self.assertEquals("Hello, &quot;World!&quot;", self.stripHtmlTags("<b>Hello, \"World!\"</b>"))
        self.assertEquals("42", self.stripHtmlTags("42"))
        # Don't merge content around tags into an entity.
        self.assertEquals("&amp;amp;", soy.utils.stripHtmlTags("&<hr>amp;"))

    def testBalanceTags(self):
        tags = ['<b>', '</b>']
        self.assertEquals('', soy.utils.balanceTags_(tags))
        self.assertEquals(['<b>', '</b>'], tags)
        tags = ['<b>']
        self.assertEquals('</b>', soy.utils.balanceTags_(tags))
        self.assertEquals(['<b>'], tags)

    def stripHtmlTagsWhitelisted(self, value):
        whitelist = {'b': 1, 'br': 1, 'ul': 1, 'li': 1, 'table': 1, 'tr': 1, 'td': 1}
        return soy.utils.stripHtmlTags(value, whitelist)

    def testStripHtmlTagsWhitelisted(self):
        self.assertEquals("<b>Hello, World!</b>", self.stripHtmlTagsWhitelisted("<b>Hello, World!</b>"))
        self.assertEquals("<b>Hello, World!</b>", self.stripHtmlTagsWhitelisted("<b onclick='evil()'>Hello, World!</b>"))
        self.assertEquals("<b>Hello, <br> World!</b>", self.stripHtmlTagsWhitelisted("<b>Hello, <br/> World!"))
        # Don't add end tags for void elements.
        self.assertEquals("<b>Hello, <br> World!</b>", self.stripHtmlTagsWhitelisted("<b>Hello, <br/> World!"))
        self.assertEquals("<b>Hello, <br> World!</b>", self.stripHtmlTagsWhitelisted("<b>Hello, <br> World!"))
        # Missing open tag.
        self.assertEquals("Hello, <br> World!", self.stripHtmlTagsWhitelisted("Hello, <br> World!"))
        # A truncated tag is not a tag.
        self.assertEquals("Hello, &lt;br", self.stripHtmlTagsWhitelisted("Hello, <br"))
        # Test boundary conditions at end of input.
        self.assertEquals("Hello, &lt;", self.stripHtmlTagsWhitelisted("Hello, <"))
        self.assertEquals("Hello, &lt;/", self.stripHtmlTagsWhitelisted("Hello, </"))
        self.assertEquals("Hello, &lt; World", self.stripHtmlTagsWhitelisted("Hello, < World"))
        # Don't be confused by attributes that merge into the tag name.
        self.assertEquals("", self.stripHtmlTagsWhitelisted("<img/onload=alert(1337)>"))
        self.assertEquals("foo", self.stripHtmlTagsWhitelisted("<i/onmouseover=alert(1337)>foo</i>"))
        self.assertEquals("AB", self.stripHtmlTagsWhitelisted("A<img/onload=alert(1337)>B"))
        # Don't create new tags from parts that were not originally adjacent.
        self.assertEquals(
            "&lt;img onload=alert(1337)",
            self.stripHtmlTagsWhitelisted("<<img/onload=alert(1337)>img onload=alert(1337)"))
        # Test external layout breakers.
        # <ul><li>Foo</ul></li> would be bad since it is equivalent to
        # <ul><li>Foo</li></ul></li>
        self.assertEquals("<ul><li>Foo</li></ul>", self.stripHtmlTagsWhitelisted("<ul><li>Foo</ul>"))
        # We put the close tags in the wrong place but in a way that is safe.
        self.assertEquals("<ul><li>1<li>2</li></li></ul>", self.stripHtmlTagsWhitelisted("<ul><li>1<li>2</ul>"))
        self.assertEquals("<table><tr><td></td></tr></table>", self.stripHtmlTagsWhitelisted("<table><tr><td>"))
        # Don't merge content around tags into an entity.
        self.assertEquals("&amp;amp;", self.stripHtmlTagsWhitelisted("&<hr>amp;"))


class TestTruncate(unittest.TestCase):

    def testTruncate(self):
        self.assertEquals('Lorem ipsum', soy.utils.truncate('Lorem ipsum', 20))
        self.assertEquals('Lorem...', soy.utils.truncate('Lorem ipsum', 8))
        self.assertEquals('Lorem ip', soy.utils.truncate('Lorem ipsum', 8, False))
        self.assertEquals('Lor', soy.utils.truncate('Lor', 3))


class TestInsertWordBreaks(unittest.TestCase):

    def testInsertWordBreaks(self):
        self.assertEquals('Lo<wbr>re<wbr>m ip<wbr>su<wbr>m', soy.utils.insertWordBreaks('Lorem ipsum', 2))
        self.assertEquals('L&amp;<wbr>re<wbr>m ip<wbr>su<wbr>m', soy.utils.insertWordBreaks('L&amp;rem ipsum', 2))
        self.assertEquals('<div>Lo<wbr>re<wbr>m ip<wbr>su<wbr>m</div>', soy.utils.insertWordBreaks('<div>Lorem ipsum</div>', 2))


class TestTemplateRegistry(unittest.TestCase):

    def testTemplate(self):
        registry = soy.utils.TemplateRegistry()
        registry.register('examples.helloWorld', lambda data: 'hi')
        output = registry.lookup('examples.helloWorld')(None)
        self.assertEquals('hi', output)

    def testVariantDelegate(self):
        registry = soy.utils.TemplateRegistry()
        registry.registerDelegate(None, 'examples.helloWorld', '', 0, lambda data: 'hello')
        registry.registerDelegate(None, 'examples.helloWorld', '', 1, lambda data: 'hi')
        registry.registerDelegate(None, 'examples.helloWorld', 'es', 0, lambda data: 'hola')
        registry.registerDelegate(None, 'examples.helloWorld', 'sk', 0, lambda data: 'ahoj')
        output = registry.lookupDelegate('examples.helloWorld', '')(None)
        self.assertEquals('hi', output)
        output = registry.lookupDelegate('examples.helloWorld', 'es')(None)
        self.assertEquals('hola', output)
        output = registry.lookupDelegate('examples.helloWorld', 'sk')(None)
        self.assertEquals('ahoj', output)
        output = registry.lookupDelegate('examples.helloWorld', 'ar')(None)
        self.assertEquals('hi', output)
        output = registry.lookupDelegate('examples.unknown', 'en')(None)
        self.assertEquals('', output)
        self.assertRaises(soy.utils.TemplateLookupError, registry.lookupDelegate, 'examples.unknown', 'en', False)

    def testPackageDelegate(self):
        registry = soy.utils.TemplateRegistry()
        registry.registerDelegate(None, 'examples.helloWorld', '', 0, lambda data: 'hi')
        registry.registerDelegate('Spanish', 'examples.helloWorld', '', 0, lambda data: 'hola')
        registry.registerDelegate('Slovak', 'examples.helloWorld', '', 0, lambda data: 'ahoj')
        output = registry.lookupDelegate('examples.helloWorld', '')(None)
        self.assertEquals('hi', output)
        output = registry.lookupDelegate('examples.helloWorld', '', packages=['Spanish'])(None)
        self.assertEquals('hola', output)
        output = registry.lookupDelegate('examples.helloWorld', '', packages=['Slovak'])(None)
        self.assertEquals('ahoj', output)

