import re

import soy.data


class Dir(object):
    RTL = -1
    UNKNOWN = 0
    LTR = 1


def bidiMarkAfterKnownDir_(bidiGlobalDir, dir, text, isHtml=False):
    """
    Returns a Unicode BiDi mark matching bidiGlobalDir (LRM or RLM) if the
    directionality or the exit directionality of text are opposite to
    bidiGlobalDir. Otherwise returns the empty string.
    If opt_isHtml, makes sure to ignore the LTR nature of the mark-up and escapes
    in text, making the logic suitable for HTML and HTML-escaped text.

    @param {number} bidiGlobalDir The global directionality context: 1 if ltr, -1
        if rtl, 0 if unknown.
    @param {number} dir text's directionality: 1 if ltr, -1 if rtl, 0 if unknown.
    @param {string} text The text whose directionality is to be estimated.
    @param {boolean=} opt_isHtml Whether text is HTML/HTML-escaped.
        Default: false.
    @return {string} A Unicode bidi mark matching bidiGlobalDir, or
        the empty string when text's overall and exit directionalities both match
        bidiGlobalDir, or bidiGlobalDir is 0 (unknown).
    @private
     """

    if bidiGlobalDir > 0 and (dir < 0 or bidiIsRtlExitText_(text, isHtml)):
        return u'\u200E' # LRM
    elif bidiGlobalDir < 0 and (dir > 0 or bidiIsLtrExitText_(text, isHtml)):
        return u'\u200F' # RLM
    return u''


def bidiStripHtmlIfNecessary_(text, isHtml=False):
    """
    Strips str of any HTML mark-up and escapes. Imprecise in several ways, but
    precision is not very important, since the result is only meant to be used
    for directionality detection.

    @param {string} str The string to be stripped.
    @param {boolean=} opt_isHtml Whether str is HTML / HTML-escaped.
        Default: false.
    @return {string} The stripped string.
    @private
    """

    if isHtml:
        return BIDI_HTML_SKIP_RE_.sub(u' ', text)
    return text


# Simplified regular expression for am HTML tag (opening or closing) or an HTML
# escape - the things we want to skip over in order to ignore their ltr
# characters.
# @type {RegExp}
# @private
BIDI_HTML_SKIP_RE_ = re.compile(r'<[^>]*>|&[^;]+;')


# A practical pattern to identify strong LTR character. This pattern is not
# theoretically correct according to unicode standard. It is simplified for
# performance and small code size.
# @type {string}
# @private
bidiLtrChars_ = \
    u'A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02B8\u0300-\u0590\u0800-\u1FFF' + \
    u'\u2C00-\uFB1C\uFDFE-\uFE6F\uFEFD-\uFFFF'


# A practical pattern to identify strong neutral and weak character. This
# pattern is not theoretically correct according to unicode standard. It is
# simplified for performance and small code size.
# @type {string}
# @private
bidiNeutralChars_ = \
    u'\u0000-\u0020!-@[-`{-\u00BF\u00D7\u00F7\u02B9-\u02FF\u2000-\u2BFF'


# A practical pattern to identify strong RTL character. This pattern is not
# theoretically correct according to unicode standard. It is simplified for
# performance and small code size.
# @type {string}
# @private
bidiRtlChars_ = u'\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC'


# Regular expressions to check if a piece of text is of RTL directionality
# on first character with strong directionality.
# @type {RegExp}
# @private
bidiRtlDirCheckRe_ = re.compile(
    r'^[^' + bidiLtrChars_ + r']*[' + bidiRtlChars_ + r']')


# Regular expressions to check if a piece of text is of neutral directionality.
# Url are considered as neutral.
# @type {RegExp}
# @private
bidiNeutralDirCheckRe_ = re.compile(
    r'^[' + bidiNeutralChars_ + r']*$|^http://')


def bidiIsRtlText_(text):
    """
    Check the directionality of the a piece of text based on the first character
    with strong directionality.
    @param {string} str string being checked.
    @return {boolean} return true if rtl directionality is being detected.
    @private
    """

    return bool(bidiRtlDirCheckRe_.search(text))


def bidiIsNeutralText_(text):
    """
    Check the directionality of the a piece of text based on the first character
    with strong directionality.
    @param {string} str string being checked.
    @return {boolean} true if all characters have neutral directionality.
    @private
    """

    return bool(bidiNeutralDirCheckRe_.search(text))


# This constant controls threshold of rtl directionality.
# @type {number}
# @private
bidiRtlDetectionThreshold_ = 0.40


def bidiRtlWordRatio_(text):
    """
    Returns the RTL ratio based on word count.
    @param {string} str the string that need to be checked.
    @return {number} the ratio of RTL words among all words with directionality.
    @private
    """

    rtlCount = 0
    totalCount = 0
    tokens = text.split(' ')
    for token in tokens:
        if bidiIsRtlText_(token):
            rtlCount += 1
            totalCount += 1
        elif bidiIsNeutralText_(token):
            totalCount += 1

    if not totalCount:
        return 0

    return 1.0 * rtlCount / totalCount


# Regular expressions to check if the last strongly-directional character in a
# piece of text is LTR.
# @type {RegExp}
# @private
bidiLtrExitDirCheckRe_ = re.compile(
    r'[' + bidiLtrChars_ + r'][^' + bidiRtlChars_ + r']*$')


# Regular expressions to check if the last strongly-directional character in a
# piece of text is RTL.
# @type {RegExp}
# @private
bidiRtlExitDirCheckRe_ = re.compile(
    r'[' + bidiRtlChars_ + r'][^' + bidiLtrChars_ + r']*$')


def bidiIsLtrExitText_(text, isHtml=False):
    """
    Check if the exit directionality a piece of text is LTR, i.e. if the last
    strongly-directional character in the string is LTR.
    @param {string} str string being checked.
    @param {boolean=} opt_isHtml Whether str is HTML / HTML-escaped.
        Default: false.
    @return {boolean} Whether LTR exit directionality was detected.
    @private
    """

    text = bidiStripHtmlIfNecessary_(text, isHtml)
    return bool(bidiLtrExitDirCheckRe_.search(text))


def bidiIsRtlExitText_(text, isHtml=False):
    """
    Check if the exit directionality a piece of text is RTL, i.e. if the last
    strongly-directional character in the string is RTL.
    @param {string} str string being checked.
    @param {boolean=} opt_isHtml Whether str is HTML / HTML-escaped.
        Default: false.
    @return {boolean} Whether RTL exit directionality was detected.
    @private
    """

    text = bidiStripHtmlIfNecessary_(text, isHtml)
    return bool(bidiRtlExitDirCheckRe_.search(text))


def detectRtlDirectionality(text, isHtml):
    """
    Check the directionality of a piece of text, return true if the piece
    of text should be laid out in RTL direction.

    @param {string} text The piece of text that need to be detected.
    @param {boolean=} opt_isHtml Whether {@code text} is HTML/HTML-escaped.
        Default: false.
    @return {boolean}
    @private
    """

    text = bidiStripHtmlIfNecessary_(text, isHtml)
    return bidiRtlWordRatio_(text) > bidiRtlDetectionThreshold_


def toDir(givenDir):
    """
    Convert a directionality given in various formats to a goog.i18n.bidi.Dir
    constant. Useful for interaction with different standards of directionality
    representation.

    @param {goog.i18n.bidi.Dir|number|boolean} givenDir Directionality given in
        one of the following formats:
        1. A goog.i18n.bidi.Dir constant.
        2. A number (positive = LRT, negative = RTL, 0 = unknown).
        3. A boolean (true = RTL, false = LTR).
    @return {goog.i18n.bidi.Dir} A goog.i18n.bidi.Dir constant matching the given
        directionality.
    """

    if isinstance(givenDir, int):
        if givenDir > 0:
            return Dir.LTR
        elif givenDir < 0:
            return Dir.RTL
        else:
            return Dir.UNKNOWN
    else:
        if givenDir:
            return Dir.RTL
        else:
            return Dir.LTR


class BidiFormatter(object):
    """
    Utility class for formatting text for display in a potentially
    opposite-directionality context without garbling.
    """

    def __init__(self, dir):
        self.dir = toDir(dir)

    def dirAttr(self, text, isHtml):
        """
        Returns 'dir="ltr"' or 'dir="rtl"', depending on {@code text}'s estimated
        directionality, if it is not the same as the context directionality.
        Otherwise, returns the empty string.

        @param {string} text Text whose directionality is to be estimated.
        @param {boolean=} isHtml Whether {@code text} is HTML / HTML-escaped.
            Default: false.
        @return {string} 'dir="rtl"' for RTL text in non-RTL context; 'dir="ltr"' for
            LTR text in non-LTR context; else, the empty string.
        """

        dir = bidiTextDir(text, isHtml)
        if dir and dir != self.dir:
            if dir < 0:
                return u'dir="rtl"'
            else:
                return u'dir="ltr"'
        return ''

    def endEdge(self):
        """
        Returns the trailing horizontal edge, i.e. "right" or "left", depending on
        the global bidi directionality.

        @return {string} "left" for RTL context and "right" otherwise.
        """

        if dir < 0:
            return u'left'
        else:
            return u'right'

    def mark(self):
        """
        Returns the Unicode BiDi mark matching the context directionality (LRM for
        LTR context directionality, RLM for RTL context directionality), or the
        empty string for neutral / unknown context directionality.

        @return {string} LRM for LTR context directionality and RLM for RTL context
            directionality.
        """

        if self.dir > 0:
            return u'\u200E'
        elif self.dir < 0:
            return u'\u200F'
        else:
            return u''

    def markAfter(self, text, isHtml):
        """
        Returns a Unicode BiDi mark matching the context directionality (LRM or RLM)
        if the directionality or the exit directionality of {@code text} are opposite
        to the context directionality. Otherwise returns the empty string.

        @param {string} text The input text.
        @param {boolean=} opt_isHtml Whether {@code text} is HTML / HTML-escaped.
            Default: false.
        @return {string} A Unicode bidi mark matching the global directionality or
            the empty string.
        """

        dir = bidiTextDir(text, isHtml)
        return bidiMarkAfterKnownDir_(self.dir, dir, text, isHtml)

    def spanWrap(self, text, placeholder):
        """
        Formats a string of unknown directionality for use in HTML output of the
        context directionality, so an opposite-directionality string is neither
        garbled nor garbles what follows it.

        @param {string} str The input text.
        @param {boolean=} placeholder This argument exists for consistency with the
            Closure Library. Specifying it has no effect.
        @return {string} Input text after applying the above processing.
        """

        text = unicode(text)
        textDir = bidiTextDir(text, True)
        reset = bidiMarkAfterKnownDir_(self.dir, textDir, text, True)
        if textDir > 0 and self.dir <= 0:
            text = u'<span dir="ltr">{0}</span>'.format(text)
        elif textDir < 0 and self.dir >= 0:
            text = u'<span dir="rtl">{0}</span>'.format(text)
        return text + reset

    def startEdge(self):
        """
        Returns the leading horizontal edge, i.e. "left" or "right", depending on
        the global bidi directionality.

        @return {string} "right" for RTL context and "left" otherwise.
        """

        if dir < 0:
            return u'right'
        else:
            return u'left'

    def unicodeWrap(self, text, placeholder):
        """
        Formats a string of unknown directionality for use in plain-text output of
        the context directionality, so an opposite-directionality string is neither
        garbled nor garbles what follows it.
        As opposed to {@link #spanWrap}, this makes use of unicode BiDi formatting
        characters. In HTML, its *only* valid use is inside of elements that do not
        allow mark-up, e.g. an 'option' tag.

        @param {string} str The input text.
        @param {boolean=} placeholder This argument exists for consistency with the
            Closure Library. Specifying it has no effect.
        @return {string} Input text after applying the above processing.
        """

        text = unicode(text)
        textDir = bidiTextDir(text, True)
        reset = bidiMarkAfterKnownDir_(self.dir, textDir, text, True)
        if textDir > 0 and self.dir <= 0:
            text = u'\u202A{0}\u202C'.format(text)
        elif textDir < 0 and self.dir >= 0:
            text = u'\u202B{0}\u202C'.format(text)
        return text + reset


# Cache of bidi formatter by context directionality, so we don't keep on
# creating new objects.
# @type {!Object.<!goog.i18n.BidiFormatter>}
# @private
bidiFormatterCache_ = {}


def getBidiFormatterInstance_(bidiGlobalDir):
    """
    Returns cached bidi formatter for bidiGlobalDir, or creates a new one.
    @param {number} bidiGlobalDir The global directionality context: 1 if ltr, -1
        if rtl, 0 if unknown.
    @return {goog.i18n.BidiFormatter} A formatter for bidiGlobalDir.
    @private
    """

    formatter = bidiFormatterCache_.get(bidiGlobalDir)
    if formatter is None:
        formatter = bidiFormatterCache_[bidiGlobalDir] = BidiFormatter(bidiGlobalDir)
    return formatter


def bidiTextDir(text, isHtml=False):
    """
    Estimate the overall directionality of text. If opt_isHtml, makes sure to
    ignore the LTR nature of the mark-up and escapes in text, making the logic
    suitable for HTML and HTML-escaped text.
    @param {string} text The text whose directionality is to be estimated.
    @param {boolean=} opt_isHtml Whether text is HTML/HTML-escaped.
        Default: false.
    @return {number} 1 if text is LTR, -1 if it is RTL, and 0 if it is neutral.
    """

    if not text:
        return 0
    return -1 if detectRtlDirectionality(text, isHtml) else 1


def bidiDirAttr(bidiGlobalDir, text, isHtml=False):
    """
    Returns 'dir="ltr"' or 'dir="rtl"', depending on text's estimated
    directionality, if it is not the same as bidiGlobalDir.
    Otherwise, returns the empty string.
    If opt_isHtml, makes sure to ignore the LTR nature of the mark-up and escapes
    in text, making the logic suitable for HTML and HTML-escaped text.
    @param {number} bidiGlobalDir The global directionality context: 1 if ltr, -1
        if rtl, 0 if unknown.
    @param {string} text The text whose directionality is to be estimated.
    @param {boolean=} opt_isHtml Whether text is HTML/HTML-escaped.
        Default: false.
    @return {soydata.SanitizedHtmlAttribute} 'dir="rtl"' for RTL text in non-RTL
        context; 'dir="ltr"' for LTR text in non-LTR context;
        else, the empty string.
    """

    return soy.data.VERY_UNSAFE.ordainSanitizedHtmlAttribute(
        getBidiFormatterInstance_(bidiGlobalDir).dirAttr(text, isHtml))


def bidiMarkAfter(bidiGlobalDir, text, isHtml=False):
    """
    Returns a Unicode BiDi mark matching bidiGlobalDir (LRM or RLM) if the
    directionality or the exit directionality of text are opposite to
    bidiGlobalDir. Otherwise returns the empty string.
    If opt_isHtml, makes sure to ignore the LTR nature of the mark-up and escapes
    in text, making the logic suitable for HTML and HTML-escaped text.
    @param {number} bidiGlobalDir The global directionality context: 1 if ltr, -1
        if rtl, 0 if unknown.
    @param {string} text The text whose directionality is to be estimated.
    @param {boolean=} opt_isHtml Whether text is HTML/HTML-escaped.
        Default: false.
    @return {string} A Unicode bidi mark matching bidiGlobalDir, or the empty
        string when text's overall and exit directionalities both match
        bidiGlobalDir, or bidiGlobalDir is 0 (unknown).
    """

    return getBidiFormatterInstance_(bidiGlobalDir).markAfter(text, isHtml)


def bidiSpanWrap(bidiGlobalDir, text):
    """
    Returns str wrapped in a <span dir="ltr|rtl"> according to its directionality
    - but only if that is neither neutral nor the same as the global context.
    Otherwise, returns str unchanged.
    Always treats str as HTML/HTML-escaped, i.e. ignores mark-up and escapes when
    estimating str's directionality.
    @param {number} bidiGlobalDir The global directionality context: 1 if ltr, -1
        if rtl, 0 if unknown.
    @param {*} str The string to be wrapped. Can be other types, but the value
        will be coerced to a string.
    @return {string} The wrapped string.
    """

    return getBidiFormatterInstance_(bidiGlobalDir).spanWrap(unicode(text), True)


def bidiUnicodeWrap(bidiGlobalDir, text):
    """
    Returns str wrapped in Unicode BiDi formatting characters according to its
    directionality, i.e. either LRE or RLE at the beginning and PDF at the end -
    but only if str's directionality is neither neutral nor the same as the
    global context. Otherwise, returns str unchanged.
    Always treats str as HTML/HTML-escaped, i.e. ignores mark-up and escapes when
    estimating str's directionality.
    @param {number} bidiGlobalDir The global directionality context: 1 if ltr, -1
        if rtl, 0 if unknown.
    @param {*} str The string to be wrapped. Can be other types, but the value
        will be coerced to a string.
    @return {string} The wrapped string.
    """

    return getBidiFormatterInstance_(bidiGlobalDir).unicodeWrap(unicode(text), True)

