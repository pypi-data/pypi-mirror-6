import imp
import importlib
import sys
import re
import urllib

import soy
import soy.escape
import soy.data


# -----------------------------------------------------------------------------
# Below are private utilities to be used by Soy-generated code only.


class TemplateLookupError(soy.SoyError):
    pass


class TemplateRegistrationError(soy.SoyError):
    pass


def _emptyTemplateFn(*args, **kwargs):
    return u''


class TemplateDelegatePackage(object):

    def __init__(self):
        self.templates = {}
        self.priorities = {}


class TemplateRegistry(object):

    def __init__(self):
        self.templates = {}
        self.delegatePackages = {}

    def register(self, name, fn):
        self.templates[name] = fn

    def lookup(self, name):
        try:
            return self.templates[name]
        except KeyError:
            raise TemplateLookupError('Could not find template {0}'.format(name))

    def registerDelegate(self, packageName, name, variant, priority, fn):
        package = self.delegatePackages.get(packageName)
        if package is None:
            package = self.delegatePackages[packageName] = TemplateDelegatePackage()

        mapKey = (name, variant)
        currPriority = package.priorities.get(mapKey)
        if currPriority is None or priority > currPriority:
            # Registering new or higher-priority function: replace registry entry.
            package.priorities[mapKey] = priority
            package.templates[mapKey] = fn
        elif priority == currPriority:
            # Registering same-priority function: error.
            raise TemplateRegistrationError(
                'Encountered two active delegates with the same priority '
                '("{0}:{1}")'.format(name, variant))
        else:
            # Registering lower-priority function: do nothing.
            pass

    def _lookupDelegateInPackages(self, name, variant, packageNames):
        if packageNames is None:
            return None
        currTemplate = None
        currPriority = -1
        for packageName in packageNames:
            package = self.delegatePackages.get(packageName)
            if package is None:
                continue
            mapKey = (name, variant)
            template = package.templates.get(mapKey)
            if template is None:
                continue
            priority = package.priorities[mapKey]
            if currTemplate is None or priority > currPriority:
                currTemplate = template
                currPriority = priority
            elif priority == currPriority:
                raise TemplateRegistrationError(
                    'Encountered two active delegates with the same priority '
                    '("{0}:{1}")'.format(name, variant))
        return currTemplate

    def lookupDelegate(self, name, variant=None, allowEmptyDefault=True, packages=None):
        template = self._lookupDelegateInPackages(name, variant, packages)
        if template is None:
            template = self._lookupDelegateInPackages(name, variant, [None])
        if template is None and variant:
            template = self._lookupDelegateInPackages(name, '', packages)
            if template is None:
                template = self._lookupDelegateInPackages(name, '', [None])

        if template is not None:
            return template
        elif allowEmptyDefault:
            return _emptyTemplateFn
        else:
            raise TemplateLookupError(
                'Found no active impl for delegate call to "{0}:{1}" (and '
                'not allowemptydefault="true").'.format(name, variant));


def getDataSingleAttr(data, key):
    if data is None or data is soy.data.UNDEFINED:
        return soy.data.UNDEFINED
    try:
        return getattr(data, key)
    except AttributeError:
        try:
            return data[key]
        except (IndexError, KeyError):
            return soy.data.UNDEFINED


def getDataSingleItem(data, key):
    if data is None or data is soy.data.UNDEFINED:
        return soy.data.UNDEFINED
    try:
        return data[key]
    except (IndexError, KeyError):
        try:
            return getattr(data, key)
        except AttributeError:
            return soy.data.UNDEFINED


def augmentMap(baseMap, additionalMap):
    augmentedMap = dict(baseMap)
    augmentedMap.update(additionalMap)
    return augmentedMap


# -----------------------------------------------------------------------------
# Soy functions.


def _round(number, ndigits=0):
    result = round(number, ndigits)
    if not ndigits:
        result = int(result)
    return result


# -----------------------------------------------------------------------------
# Escape/filter/normalize.


def escapeHtml(value):
    """
    Escapes HTML special characters in a string. Escapes double quote '"' in
    addition to '&', '<', and '>' so that a string can be included in an HTML
    tag attribute value within double quotes.
    Will emit known safe HTML as-is.

    :param value: The string-like value to be escaped. May not be a string,
        but the value will be coerced to a string.
    :returns: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedHtml):
        return value.content
    if hasattr(value, '__html__'): # compatibility with jinja/mako
        return value.__html__()
    return soy.escape.escapeHtmlHelper(value)


def cleanHtml(value):
    """
    Strips unsafe tags to convert a string of untrusted HTML into HTML that
    is safe to embed.

    :param value: The string-like value to be escaped. May not be a string,
        but the value will be coerced to a string.
    :returns: A sanitized and normalized version of value.
    """

    if isinstance(value, soy.data.SanitizedHtml):
        return value.content
    if hasattr(value, '__html__'): # compatibility with jinja/mako
        return value.__html__()
    return stripHtmlTags(value, soy.escape.SAFE_TAG_WHITELIST_)


def escapeHtmlRcdata(value):
    """
    Escapes HTML special characters in a string so that it can be embedded in
    RCDATA.

    Escapes HTML special characters so that the value will not prematurely end
    the body of a tag like ``<textarea>`` or ``<title>``. RCDATA tags
    cannot contain other HTML entities, so it is not strictly necessary to escape
    HTML special characters except when part of that text looks like an HTML
    entity or like a close tag : ``</textarea>``.

    Will normalize known safe HTML to make sure that sanitized HTML (which could
    contain an innocuous ``</textarea>`` don't prematurely end an RCDATA
    element.

    :param value: The string-like value to be escaped. May not be a string,
        but the value will be coerced to a string.
    :returns: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedHtml):
        return soy.escape.normalizeHtmlHelper(value.content)
    if hasattr(value, '__html__'):
        return soy.escape.normalizeHtmlHelper(value.__html__())
    return soy.escape.escapeHtmlHelper(value)


#
# Matches any/only HTML5 void elements' start tags.
# See http://www.w3.org/TR/html-markup/syntax.html#syntax-elements
#
HTML5_VOID_ELEMENTS_ = re.compile(
    '^<(?:area|base|br|col|command|embed|hr|img|input' +
    '|keygen|link|meta|param|source|track|wbr)\\b')


def stripHtmlTags(value, safeTags=None, rawSpacesAllowed=True):
    """
    Removes HTML tags from a string of known safe HTML.
    If tagWhitelist is not specified or is empty, then
    the result can be used as an attribute value.

    :param value: The HTML to be escaped. May not be a string, but the
        value will be coerced to a string.
    :param safeTags: Set with lower-case tag names for
        each element that is allowed in the output.
    :param rawSpacesAllowed: True if spaces are allowed in the output
        unescaped as is the case when the output is embedded in a regular
        text node, or in a quoted attribute.
    :returns: A representation of value without disallowed tags,
        HTML comments, or other non-text content.
    """

    if rawSpacesAllowed:
        normalizeHelper = soy.escape.normalizeHtmlHelper
    else:
        normalizeHelper = soy.escape.normalizeHtmlNospaceHelper

    # Escapes '[' so that we can use [123] below to mark places where tags
    # have been removed.
    html = re.sub('\[', '&#91;', unicode(value))

    if safeTags is None:
        # If we have no white-list, then use a fast track which elides all tags.
        html = soy.escape.HTML_TAG_REGEX_.sub('[]', html)
        # This is just paranoia since callers should normalize the result
        # anyway, but if they didn't, it would be necessary to ensure that
        # after the first replace non-tag uses of < do not recombine into
        # tags as in "<<foo>script>alert(1337)</<foo>script>".
        html = normalizeHelper(html)
        # More aggressively normalize ampersands at the end of a chunk so that
        # "&<b>amp;</b>" -> "&amp;amp;" instead of "&amp;".
        html = html.replace('&[]', '&amp;').replace('[]', '')
        return html

    # Consider all uses of '<' and replace whitelisted tags with markers like
    # [1] which are indices into a list of approved tag names.
    # Replace all other uses of < and > with entities.
    tags = []
    def stripTags(match):
        tagName = match.group(1)
        if tagName:
            tagName = tagName.lower()
            if tagName in safeTags:
                tok = match.group(0)
                start = '</' if tok[1] == '/' else '<'
                index = len(tags)
                tags.append(start + tagName + '>')
                return '[{0}]'.format(index)
        return '[]'
    html = soy.escape.HTML_TAG_REGEX_.sub(stripTags, html)

    # Escape HTML special characters. Now there are no '<' in html that could
    # start a tag.
    html = normalizeHelper(html)

    # More aggressively normalize ampersands at the end of a chunk so that
    # "&<b>amp;</b>" -> "&amp;amp;" instead of "&amp;".
    html = html.replace('&[]', '&amp;').replace('[]', '')

    finalCloseTags = balanceTags_(tags)

    # Now html contains no tags or less-than characters that could become
    # part of a tag via a replacement operation and tags only contains
    # approved tags.
    # Reinsert the white-listed tags.
    def replaceTags(match):
        index = int(match.group(1))
        return tags[index]
    html = re.sub('\[(\d+)\]', replaceTags, html)

    # Close any still open tags.
    # This prevents unclosed formatting elements like <ol> and <table> from
    # breaking the layout of containing HTML.
    return html + finalCloseTags


def balanceTags_(tags):
    """
    Throw out any close tags that don't correspond to start tags.
    If ``<table>`` is used for formatting, embedded HTML shouldn't be able
    to use a mismatched ``</table>`` to break page layout.

    :param tags: an array of tags that will be modified in place
       include tags, the empty string, or concatenations of empty tags.
    :returns: zero or more closed tags that close all elements that are
       opened in tags but not closed.
    """

    open = []
    for i, tag in enumerate(tags):
        if tag[1] == '/':
            openTagIndex = len(open) - 1
            # NOTE: This is essentially "rindex", but Python doesn't support that on lists
            while openTagIndex > 0 and open[openTagIndex] != tag:
                openTagIndex -= 1
            if openTagIndex < 0:
                tags[i] = '' # Drop close tag.
            else:
                tags[i] = ''.join(reversed(open[openTagIndex:]))
                open = open[:openTagIndex]
        elif not HTML5_VOID_ELEMENTS_.search(tag):
            open.append('</' + tag[1:])
    return ''.join(reversed(open))


def escapeHtmlAttribute(value):
    """
    Escapes HTML special characters in an HTML attribute value.

    :param value: The HTML to be escaped. May not be a string, but the
       value will be coerced to a string.
    :returns: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedHtml):
        return stripHtmlTags(value.content)
    if hasattr(value, '__html__'): # compatibility with jinja/mako
        return stripHtmlTags(value.__html__())
    return soy.escape.escapeHtmlHelper(value)


def escapeHtmlAttributeNospace(value):
    """
    Escapes HTML special characters in an HTML attribute value.

    :param value: The HTML to be escaped. May not be a string, but the
       value will be coerced to a string.
    :returns: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedHtml):
        return stripHtmlTags(value.content, rawSpacesAllowed=False)
    if hasattr(value, '__html__'): # compatibility with jinja/mako
        return stripHtmlTags(value.__html__(), rawSpacesAllowed=False)
    return soy.escape.escapeHtmlNospaceHelper(value)


def filterHtmlAttributes(value):
    """
    Filters out strings that cannot be a substring of a valid HTML attribute.

    Note the input is expected to be key=value pairs.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: A valid HTML attribute name part or name/value pair.
        ``"zSoyz"`` if the input is invalid.
    """

    if isinstance(value, soy.data.SanitizedHtmlAttribute):
        # Add a space at the end to ensure this won't get merged into following
        # attributes, unless the interpretation is unambiguous (ending with quotes
        # or a space).
        return re.sub(r'([^"\'\s])$', r'\1 ', value.content)
    # TODO: Dynamically inserting attributes that aren't marked as trusted is
    # probably unnecessary.  Any filtering done here will either be inadequate
    # for security or not flexible enough.  Having clients use kind="attributes"
    # in parameters seems like a wiser idea.
    return soy.escape.filterHtmlAttributesHelper(value)


def filterHtmlElementName(value):
    """
    Filters out strings that cannot be a substring of a valid HTML element name.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: A valid HTML element name part.
        ``"zSoyz"`` if the input is invalid.
    """

    # NOTE: We don't accept any SanitizedContent here. HTML indicates valid
    # PCDATA, not tag names. A sloppy developer shouldn't be able to cause an
    # exploit:
    # ... {let userInput}script src=http://evil.com/evil.js{/let} ...
    # ... {param tagName kind="html"}{$userInput}{/param} ...
    # ... <{$tagName}>Hello World</{$tagName}>
    return soy.escape.filterHtmlElementNameHelper(value)


def escapeJsString(value):
    """
    Escapes characters in the value to make it valid content for a JS string
    literal.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedJsStrChars):
        return value.content
    return soy.escape.escapeJsStringHelper(value)


def escapeJsValue(value):
    """
    Encodes a value as a JavaScript literal.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: A JavaScript code representation of the input.
    """

    # We surround values with spaces so that they can't be interpolated into
    # identifiers by accident.
    # We could use parentheses but those might be interpreted as a function call.
    if value is None:
        # Java returns null from maps where there is no corresponding key while
        # JS returns undefined.
        # We always output null for compatibility with Java which does not have a
        # distinct undefined value.
        return ' null '
    if isinstance(value, soy.data.SanitizedJs):
        return value.content
    if isinstance(value, bool):
        return ' {0} '.format(str(value).lower())
    if isinstance(value, (int, float)):
        return ' {0} '.format(str(value))
    return "'" + soy.escape.escapeJsStringHelper(value) + "'"


def escapeJsRegex(value):
    """
    Escapes characters in the string to make it valid content for a JS regular
    expression literal.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: An escaped version of value.
    """

    return soy.escape.escapeJsRegexHelper(value)


def escapeUri(value):
    """
    Escapes a string so that it can be safely included in a URI.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedUri):
        return normalizeUri(value.content)
    return urllib.quote(unicode(value).encode('utf8'), safe='~')


def normalizeUri(value):
    """
    Removes rough edges from a URI by escaping any raw HTML/JS string delimiters.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: An escaped version of value.
    """

    return soy.escape.normalizeUriHelper(value)


def filterNormalizeUri(value):
    """
    Vets a URI's protocol and removes rough edges from a URI by escaping
    any raw HTML/JS string delimiters.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :return: An escaped version of value.
    """

    if isinstance(value, soy.data.SanitizedUri):
        return normalizeUri(value.content)
    return soy.escape.filterNormalizeUriHelper(value)


def escapeCssString(value):
    """
    Escapes a string so it can safely be included inside a quoted CSS string.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: An escaped version of value.
    """

    return soy.escape.escapeCssStringHelper(value)


def filterCssValue(value):
    """
    Encodes a value as a CSS identifier part, keyword, or quantity.

    :param value: The value to escape. May not be a string, but the value
        will be coerced to a string.
    :returns: A safe CSS identifier part, keyword, or quanitity.
    """

    if isinstance(value, soy.data.SanitizedCss):
        return value.content
    if value is None:
        return u''
    return soy.escape.filterCssValueHelper(value)


def filterNoAutoescape(value):
    """
    Sanity-checks noAutoescape input for explicitly tainted content.

    ``UnsanitizedText`` is used to explicitly mark input that was never
    meant to be used unescaped.

    :param value: The value to filter.
    :returns: The value, that we dearly hope will not cause an attack.
    """
    if isinstance(value, soy.data.UnsanitizedText):
        return 'zSoyz'
    return unicode(value)


# -----------------------------------------------------------------------------
# Basic directives/functions.


def changeNewlineToBr(value, xml=False):
    """
    Converts \r\n, \r, and \n to <br>s
    :param value: The string in which to convert newlines.
    :param xml: Whether to use XML compatible tags.
    :returns: A copy of ``value`` with converted newlines.
    """

    return re.sub(r'(\r\n|\r|\n)', '<br />' if xml else '<br>', unicode(value))


def insertWordBreaks(value, maxCharsBetweenWordBreaks):
    """
    Inserts word breaks ('wbr' tags) into a HTML string at a given interval. The
    counter is reset if a space is encountered. Word breaks aren't inserted into
    HTML tags or entities. Entites count towards the character count; HTML tags
    do not.

    :param value: The HTML string to insert word breaks into. Can be other
        types, but the value will be coerced to a string.
    :param maxCharsBetweenWordBreaks: Maximum number of non-space
        characters to allow before adding a word break.
    :returns: The string including word breaks.
    """

    value = unicode(value)
    result = []

    # These variables keep track of important state inside str.
    isInTag = False  # whether we're inside an HTML tag
    isMaybeInEntity = False  # whether we might be inside an HTML entity
    numCharsWithoutBreak = 0  # number of chars since last word break
    flushIndex = 0  # index of first char not yet flushed to resultArr

    for i, char in enumerate(value):
        charCode = ord(char)

        # If hit maxCharsBetweenWordBreaks, and not space next, then add <wbr>.
        if numCharsWithoutBreak >= maxCharsBetweenWordBreaks and charCode != 32: # space
            result.append(value[flushIndex:i])
            flushIndex = i
            result.append("<wbr>")
            numCharsWithoutBreak = 0

        if isInTag:
            # If inside an HTML tag and we see '>', it's the end of the tag.
            if charCode == 62:
                isInTag = False
        elif isMaybeInEntity:
            # Inside an entity, a ';' is the end of the entity.
            # The entity that just ended counts as one char, so increment
            # numCharsWithoutBreak.
            if charCode == 59: # ';'
                isMaybeInEntity = False
                numCharsWithoutBreak += 1
            # If maybe inside an entity and we see '<', we weren't actually in
            # an entity. But now we're inside and HTML tag.
            elif charCode == 60: # '<'
                isMaybeInEntity = False
                isInTag = True
            # If maybe inside an entity and we see ' ', we weren't actually in
            # an entity. Just correct the state and reset the
            # numCharsWithoutBreak since we just saw a space.
            elif charCode == 32: # ' '
                isMaybeInEntity = False
                numCharsWithoutBreak = 0
        else:
            # When not within a tag or an entity and we see '<', we're now
            # inside an HTML tag.
            if charCode == 60: # '<'
                isInTag = True
            # When not within a tag or an entity and we see '&', we might be
            # inside an entity.
            elif charCode == 38: # '&'
                isMaybeInEntity = True
            # When we see a space, reset the numCharsWithoutBreak count.
            elif charCode == 32: # ' '
                numCharsWithoutBreak = 0
            # When we see a non-space, increment the numCharsWithoutBreak.
            else:
                numCharsWithoutBreak += 1

    result.append(value[flushIndex:])

    return u"".join(result)


def truncate(value, maxLen, doAddEllipsis=True):
    """
    Truncates a string to a given max length (if it's currently longer),
    optionally adding ellipsis at the end.

    :param value: The string to truncate. Can be other types, but the value will
        be coerced to a string.
    :param maxLen: The maximum length of the string after truncation
        (including ellipsis, if applicable).
    :param doAddEllipsis: Whether to add ellipsis if the string needs
        truncation.
    :returns: The string after truncation.
    """

    value = unicode(value)
    if len(value) <= maxLen:
        return value

    if doAddEllipsis:
        if maxLen > 3:
            maxLen -= 3
        else:
            doAddEllipsis = False

    if isHighSurrogate_(ord(value[maxLen-1])) and isLowSurrogate_(ord(value[maxLen])):
        maxLen -= 1

    value = value[:maxLen]

    if doAddEllipsis:
        value += u'...'

    return value


def isHighSurrogate_(ch):
    """
    Private helper for truncate() to check whether a char is a high surrogate.
    """
    return 0xD800 <= ch and ch <= 0xDBFF


def isLowSurrogate_(ch):
    """
    Private helper for truncate() to check whether a char is a low surrogate.
    """
    return 0xDC00 <= ch and ch <= 0xDFFF

