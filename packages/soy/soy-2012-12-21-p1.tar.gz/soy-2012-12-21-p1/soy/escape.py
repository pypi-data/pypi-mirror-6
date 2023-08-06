import re

# START GENERATED CODE FOR ESCAPERS.

#
# Maps charcters to the escaped versions for the named escape directives.
#
ESCAPE_MAP_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_ = {
    u'\x00': u'&#0;',
    u'\"': u'&quot;',
    u'&': u'&amp;',
    u'\'': u'&#39;',
    u'<': u'&lt;',
    u'>': u'&gt;',
    u'\t': u'&#9;',
    u'\n': u'&#10;',
    u'\x0b': u'&#11;',
    u'\x0c': u'&#12;',
    u'\r': u'&#13;',
    u' ': u'&#32;',
    u'-': u'&#45;',
    u'/': u'&#47;',
    u'=': u'&#61;',
    u'`': u'&#96;',
    u'\x85': u'&#133;',
    u'\xa0': u'&#160;',
    u'\u2028': u'&#8232;',
    u'\u2029': u'&#8233;',
}

#
# A function that can be used with re.sub.
#
def REPLACER_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_(match):
    return ESCAPE_MAP_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_[match.group(0)]


#
# Maps charcters to the escaped versions for the named escape directives.
#
ESCAPE_MAP_FOR_ESCAPE_JS_STRING__AND__ESCAPE_JS_REGEX_ = {
    u'\x00': u'\\x00',
    u'\x08': u'\\x08',
    u'\t': u'\\t',
    u'\n': u'\\n',
    u'\x0b': u'\\x0b',
    u'\x0c': u'\\f',
    u'\r': u'\\r',
    u'\"': u'\\x22',
    u'&': u'\\x26',
    u'\'': u'\\x27',
    u'/': u'\\/',
    u'<': u'\\x3c',
    u'=': u'\\x3d',
    u'>': u'\\x3e',
    u'\\': u'\\\\',
    u'\x85': u'\\x85',
    u'\u2028': u'\\u2028',
    u'\u2029': u'\\u2029',
    u'$': u'\\x24',
    u'(': u'\\x28',
    u')': u'\\x29',
    u'*': u'\\x2a',
    u'+': u'\\x2b',
    u',': u'\\x2c',
    u'-': u'\\x2d',
    u'.': u'\\x2e',
    u':': u'\\x3a',
    u'?': u'\\x3f',
    u'[': u'\\x5b',
    u']': u'\\x5d',
    u'^': u'\\x5e',
    u'{': u'\\x7b',
    u'|': u'\\x7c',
    u'}': u'\\x7d',
}

#
# A function that can be used with re.sub.
#
def REPLACER_FOR_ESCAPE_JS_STRING__AND__ESCAPE_JS_REGEX_(match):
    return ESCAPE_MAP_FOR_ESCAPE_JS_STRING__AND__ESCAPE_JS_REGEX_[match.group(0)]


#
# Maps charcters to the escaped versions for the named escape directives.
#
ESCAPE_MAP_FOR_ESCAPE_CSS_STRING_ = {
    u'\x00': u'\\0 ',
    u'\x08': u'\\8 ',
    u'\t': u'\\9 ',
    u'\n': u'\\a ',
    u'\x0b': u'\\b ',
    u'\x0c': u'\\c ',
    u'\r': u'\\d ',
    u'\"': u'\\22 ',
    u'&': u'\\26 ',
    u'\'': u'\\27 ',
    u'(': u'\\28 ',
    u')': u'\\29 ',
    u'*': u'\\2a ',
    u'/': u'\\2f ',
    u':': u'\\3a ',
    u';': u'\\3b ',
    u'<': u'\\3c ',
    u'=': u'\\3d ',
    u'>': u'\\3e ',
    u'@': u'\\40 ',
    u'\\': u'\\5c ',
    u'{': u'\\7b ',
    u'}': u'\\7d ',
    u'\x85': u'\\85 ',
    u'\xa0': u'\\a0 ',
    u'\u2028': u'\\2028 ',
    u'\u2029': u'\\2029 ',
}

#
# A function that can be used with re.sub.
#
def REPLACER_FOR_ESCAPE_CSS_STRING_(match):
    return ESCAPE_MAP_FOR_ESCAPE_CSS_STRING_[match.group(0)]


#
# Maps charcters to the escaped versions for the named escape directives.
#
ESCAPE_MAP_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_ = {
    u'\x00': u'%00',
    u'\x01': u'%01',
    u'\x02': u'%02',
    u'\x03': u'%03',
    u'\x04': u'%04',
    u'\x05': u'%05',
    u'\x06': u'%06',
    u'\x07': u'%07',
    u'\x08': u'%08',
    u'\t': u'%09',
    u'\n': u'%0A',
    u'\x0b': u'%0B',
    u'\x0c': u'%0C',
    u'\r': u'%0D',
    u'\x0e': u'%0E',
    u'\x0f': u'%0F',
    u'\x10': u'%10',
    u'\x11': u'%11',
    u'\x12': u'%12',
    u'\x13': u'%13',
    u'\x14': u'%14',
    u'\x15': u'%15',
    u'\x16': u'%16',
    u'\x17': u'%17',
    u'\x18': u'%18',
    u'\x19': u'%19',
    u'\x1a': u'%1A',
    u'\x1b': u'%1B',
    u'\x1c': u'%1C',
    u'\x1d': u'%1D',
    u'\x1e': u'%1E',
    u'\x1f': u'%1F',
    u' ': u'%20',
    u'\"': u'%22',
    u'\'': u'%27',
    u'(': u'%28',
    u')': u'%29',
    u'<': u'%3C',
    u'>': u'%3E',
    u'\\': u'%5C',
    u'{': u'%7B',
    u'}': u'%7D',
    u'\x7f': u'%7F',
    u'\x85': u'%C2%85',
    u'\xa0': u'%C2%A0',
    u'\u2028': u'%E2%80%A8',
    u'\u2029': u'%E2%80%A9',
    u'\uff01': u'%EF%BC%81',
    u'\uff03': u'%EF%BC%83',
    u'\uff04': u'%EF%BC%84',
    u'\uff06': u'%EF%BC%86',
    u'\uff07': u'%EF%BC%87',
    u'\uff08': u'%EF%BC%88',
    u'\uff09': u'%EF%BC%89',
    u'\uff0a': u'%EF%BC%8A',
    u'\uff0b': u'%EF%BC%8B',
    u'\uff0c': u'%EF%BC%8C',
    u'\uff0f': u'%EF%BC%8F',
    u'\uff1a': u'%EF%BC%9A',
    u'\uff1b': u'%EF%BC%9B',
    u'\uff1d': u'%EF%BC%9D',
    u'\uff1f': u'%EF%BC%9F',
    u'\uff20': u'%EF%BC%A0',
    u'\uff3b': u'%EF%BC%BB',
    u'\uff3d': u'%EF%BC%BD',
}

#
# A function that can be used with re.sub.
#
def REPLACER_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_(match):
    return ESCAPE_MAP_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_[match.group(0)]


#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_ESCAPE_HTML_ = re.compile(u'[\x00\"&\'<>]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_NORMALIZE_HTML_ = re.compile(u'[\x00\"\'<>]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_ESCAPE_HTML_NOSPACE_ = re.compile(u'[\x00\t-\r \"&\'\\-/<->`\x85\xa0\u2028\u2029]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_NORMALIZE_HTML_NOSPACE_ = re.compile(u'[\x00\t-\r \"\'\\-/<->`\x85\xa0\u2028\u2029]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_ESCAPE_JS_STRING_ = re.compile(u'[\x00\x08-\r\"&\'/<->\\\\\x85\u2028\u2029]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_ESCAPE_JS_REGEX_ = re.compile(u'[\x00\x08-\r\"\\$&-/\\:<-\\?\\[-\\^\\{-\\}\x85\u2028\u2029]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_ESCAPE_CSS_STRING_ = re.compile(u'[\x00\x08-\r\"&-\\*/\\:->@\\\\\\{\\}\x85\xa0\u2028\u2029]')

#
# Matches characters that need to be escaped for the named directives.
#
MATCHER_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_ = re.compile(u'[\x00- \"\'-\\)<>\\\\\\{\\}\x7f\x85\xa0\u2028\u2029\uff01\uff03\uff04\uff06-\uff0c\uff0f\uff1a\uff1b\uff1d\uff1f\uff20\uff3b\uff3d]')

#
# A pattern that vets values produced by the named directives.
#
FILTER_FOR_FILTER_CSS_VALUE_ = re.compile(u'^(?!-*(?:expression|(?:moz-)?binding))(?:[.#]?-?(?:[_a-z0-9-]+)(?:-[_a-z0-9-]+)*-?|-?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[a-z]{1,2}|%)?|!important|)$', re.IGNORECASE)

#
# A pattern that vets values produced by the named directives.
#
FILTER_FOR_FILTER_NORMALIZE_URI_ = re.compile(u'^(?:(?:https?|mailto):|[^&:\\/?#]*(?:[\\/?#]|$))', re.IGNORECASE)

#
# A pattern that vets values produced by the named directives.
#
FILTER_FOR_FILTER_HTML_ATTRIBUTES_ = re.compile(u'^(?!style|on|action|archive|background|cite|classid|codebase|data|dsync|href|longdesc|src|usemap)(?:[a-z0-9_$:-]*)$', re.IGNORECASE)

#
# A pattern that vets values produced by the named directives.
#
FILTER_FOR_FILTER_HTML_ELEMENT_NAME_ = re.compile(u'^(?!script|style|title|textarea|xmp|no)[a-z0-9_$:-]*$', re.IGNORECASE)


#
# A helper for the Soy directive |escapeHtml
#
def escapeHtmlHelper(value):
    value = unicode(value)
    return MATCHER_FOR_ESCAPE_HTML_.sub(
        REPLACER_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_,
        value)


#
# A helper for the Soy directive |normalizeHtml
#
def normalizeHtmlHelper(value):
    value = unicode(value)
    return MATCHER_FOR_NORMALIZE_HTML_.sub(
        REPLACER_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_,
        value)


#
# A helper for the Soy directive |escapeHtmlNospace
#
def escapeHtmlNospaceHelper(value):
    value = unicode(value)
    return MATCHER_FOR_ESCAPE_HTML_NOSPACE_.sub(
        REPLACER_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_,
        value)


#
# A helper for the Soy directive |normalizeHtmlNospace
#
def normalizeHtmlNospaceHelper(value):
    value = unicode(value)
    return MATCHER_FOR_NORMALIZE_HTML_NOSPACE_.sub(
        REPLACER_FOR_ESCAPE_HTML__AND__NORMALIZE_HTML__AND__ESCAPE_HTML_NOSPACE__AND__NORMALIZE_HTML_NOSPACE_,
        value)


#
# A helper for the Soy directive |escapeJsString
#
def escapeJsStringHelper(value):
    value = unicode(value)
    return MATCHER_FOR_ESCAPE_JS_STRING_.sub(
        REPLACER_FOR_ESCAPE_JS_STRING__AND__ESCAPE_JS_REGEX_,
        value)


#
# A helper for the Soy directive |escapeJsRegex
#
def escapeJsRegexHelper(value):
    value = unicode(value)
    return MATCHER_FOR_ESCAPE_JS_REGEX_.sub(
        REPLACER_FOR_ESCAPE_JS_STRING__AND__ESCAPE_JS_REGEX_,
        value)


#
# A helper for the Soy directive |escapeCssString
#
def escapeCssStringHelper(value):
    value = unicode(value)
    return MATCHER_FOR_ESCAPE_CSS_STRING_.sub(
        REPLACER_FOR_ESCAPE_CSS_STRING_,
        value)


#
# A helper for the Soy directive |filterCssValue
#
def filterCssValueHelper(value):
    value = unicode(value)
    if not FILTER_FOR_FILTER_CSS_VALUE_.search(value):
        return 'zSoyz'
    return value


#
# A helper for the Soy directive |normalizeUri
#
def normalizeUriHelper(value):
    value = unicode(value)
    return MATCHER_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_.sub(
        REPLACER_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_,
        value)


#
# A helper for the Soy directive |filterNormalizeUri
#
def filterNormalizeUriHelper(value):
    value = unicode(value)
    if not FILTER_FOR_FILTER_NORMALIZE_URI_.search(value):
        return '#zSoyz'
    return MATCHER_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_.sub(
        REPLACER_FOR_NORMALIZE_URI__AND__FILTER_NORMALIZE_URI_,
        value)


#
# A helper for the Soy directive |filterHtmlAttributes
#
def filterHtmlAttributesHelper(value):
    value = unicode(value)
    if not FILTER_FOR_FILTER_HTML_ATTRIBUTES_.search(value):
        return 'zSoyz'
    return value


#
# A helper for the Soy directive |filterHtmlElementName
#
def filterHtmlElementNameHelper(value):
    value = unicode(value)
    if not FILTER_FOR_FILTER_HTML_ELEMENT_NAME_.search(value):
        return 'zSoyz'
    return value


#
# Matches all tags, HTML comments, and DOCTYPEs in tag soup HTML.
# By removing these, and replacing any '<' or '>' characters with
# entities we guarantee that the result can be embedded into a
# an attribute without introducing a tag boundary.
#
HTML_TAG_REGEX_ = re.compile(u'<(?:!|/?([a-zA-Z][a-zA-Z0-9:\\-]*))(?:[^>\'\"]|\"[^\"]*\"|\'[^\']*\')*>')


#
# Maps lower-case names of innocuous tags to 1.
#
SAFE_TAG_WHITELIST_ = set([u'b', u'br', u'em', u'i', u's', u'sub', u'sup', u'u', ])

# END GENERATED CODE
