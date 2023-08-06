"""
Defines typed strings, e.g. an HTML string ``"a<b>c"`` is
semantically distinct from the plain text string ``"a<b>c"`` and smart
templates can take that distinction into account.
"""

class SanitizedContent(object):

    def __init__(self, content):
        self.content = content

    def __unicode__(self):
        return self.content


class SanitizedHtml(SanitizedContent):
    """
    The content is a string of HTML that can safely be embedded in a PCDATA
    context in your app.  If you would be surprised to find that an HTML
    sanitizer produced ``s`` (e.g.  it runs code or fetches bad URLs) and
    you wouldn't write a template that produces ``s`` on security or privacy
    grounds, then don't pass ``s`` here.
    """


class SanitizedJs(SanitizedContent):
    """
    The content is Javascript source that when evaluated does not execute any
    attacker-controlled scripts.
    """


class SanitizedJsStrChars(SanitizedContent):
    """
    The content can be safely inserted as part of a single- or double-quoted
    string without terminating the string.
    """


class SanitizedUri(SanitizedContent):
    """
    The content is a URI chunk that the caller knows is safe to emit in a
    template.
    """


class SanitizedHtmlAttribute(SanitizedContent):
    """
    The content should be safely embeddable within an open tag, such as a
    key="value" pair.
    """


class SanitizedCss(SanitizedContent):
    """
    The content is non-attacker-exploitable CSS, such as ``color:#c3d9ff``.
    """


class UnsanitizedText(SanitizedContent):
    """
    Unsanitized plain text string.

    While all strings are effectively safe to use as a plain text, there are no
    guarantees about safety in any other context such as HTML. This is
    sometimes used to mark that should never be used unescaped.
    """

    def __init__(self, content):
        self.content = unicode(content)


def markUnsanitizedText(content):
    return UnsanitizedText(content)


class VeryUnsafe(object):

    def __init__(self, sanitizedClasses):
        for sanitizedClass in sanitizedClasses:
            funcName = 'ordain' + sanitizedClass.__name__
            setattr(self, funcName, sanitizedClass)

VERY_UNSAFE = VeryUnsafe([
    SanitizedHtml,
    SanitizedJs,
    SanitizedJsStrChars,
    SanitizedUri,
    SanitizedHtmlAttribute,
    SanitizedCss,
])


class Undefined(object):

    def __repr__(self):
        return 'Undefined'

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        return False

UNDEFINED = Undefined()

