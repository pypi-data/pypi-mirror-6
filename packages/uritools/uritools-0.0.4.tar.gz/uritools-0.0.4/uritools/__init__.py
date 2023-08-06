"""RFC 3986 compliant, Unicode-aware, scheme-agnostic replacement for
urlparse.

The urlparse module is not compliant with RFC 3986, and is generally
unusable with custom (private) URI schemes.  This module provides
compliant replacements for urlsplit and urlunsplit, as well as a
convenient way to compose URIs.

"""
from collections import namedtuple
import re

__version__ = '0.0.4'

# RFC 3986: 2.2. Reserved Characters
GEN_DELIMS = ':/?#[]@'

SUB_DELIMS = "!$&'()*+,;="

RESERVED = GEN_DELIMS + SUB_DELIMS

# RFC 3986: 2.3. Unreserved Characters
UNRESERVED = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '0123456789'
    '_.-~'
)

# RFC 3986: Appendix B
RE = re.compile(r"""
(?:([^:/?#]+):)?  # scheme
(?://([^/?#]*))?  # authority
([^?#]*)          # path
(?:\?([^#]*))?    # query
(?:\#(.*))?       # fragment
""", flags=(re.VERBOSE))
"""Regular expression to split URIs into components."""


def uriencode(s, safe='', encoding='utf-8'):
    from urllib import quote
    return quote(s.encode(encoding), UNRESERVED + safe)


def uridecode(s, encoding='utf-8'):
    from urllib import unquote
    return unquote(s).decode(encoding)


class SplitResult(namedtuple('SplitResult', 'scheme authority path query fragment')):
    """Extend `namedtuple` to hold `urisplit()` results.

    Attributes:
        :scheme: URI scheme or None if not present
        :authority: URI authority component or None if not present
        :path: URI path component, always present but may be empty
        :query: URI query component or None if not present
        :fragment: URI fragment component or None if not present

    """

    def getscheme(self, default=None):
        if self.scheme is None:
            return default
        return uridecode(self.scheme, encoding='ascii')

    def getauthority(self, default=None, encoding='utf-8'):
        if self.authority is None:
            return default
        return uridecode(self.authority, encoding=encoding)

    def getpath(self, encoding='utf-8'):
        return uridecode(self.path, encoding=encoding)

    def getquery(self, default=None, encoding='utf-8'):
        if self.query is None:
            return default
        return uridecode(self.query, encoding=encoding)

    def getfragment(self, default=None, encoding='utf-8'):
        if self.fragment is None:
            return default
        return uridecode(self.fragment, encoding=encoding)

    def geturi(self):
        return uriunsplit(self)


def urisplit(uristring):
    """Split a URI string into a named tuple with five components::

      <scheme>://<authority>/<path>?<query>#<fragment>

    The returned object is an instance of `SplitResult`.

    """
    return SplitResult(*RE.match(uristring).groups())


def uriunsplit(parts):
    """Combine the elements of a tuple as returned by `urisplit()` into a
    complete URI as a string.

    The `parts` argument can be any five-item iterable.

    """

    scheme, authority, path, query, fragment = parts
    uri = ''

    if scheme is not None:
        if any(c in ':/?#' for c in scheme):
            raise ValueError('Reserved character in %r' % scheme)
        uri += scheme + ':'

    if authority is not None:
        if any(c in '/?#' for c in authority):
            raise ValueError('Reserved character in %r' % authority)
        uri += '//' + authority

    if path is None:
        raise ValueError('URI path must be present if empty')
    if any(c in '?#' for c in path):
        raise ValueError('Reserved character in %r' % path)
    # RFC 3986 3.3: If a URI contains an authority component, then the
    # path component must either be empty or begin with a slash ("/")
    # character.  If a URI does not contain an authority component,
    # then the path cannot begin with two slash characters ("//")
    if authority and path and not path.startswith('/'):
        raise ValueError('Cannot use path %r with authority' % path)
    if not authority and path.startswith('//'):
        raise ValueError('Cannot use path %r without authority' % path)
    uri += path

    if query is not None:
        if '#' in query:
            raise ValueError('Reserved character in %r' % query)
        uri += '?' + query

    if fragment is not None:
        uri += '#' + fragment

    return uri


def uricompose(scheme=None, authority=None, path='', query=None,
               fragment=None, encoding='utf-8'):
    """Compose a URI string from its components.

    """

    if scheme is not None:
        scheme = uriencode(scheme, encoding='ascii')
    if authority is not None:
        authority = uriencode(authority, SUB_DELIMS + ':@', encoding)
    if path is not None:
        path = uriencode(path, SUB_DELIMS + ':@/', encoding)
    if query is not None:
        query = uriencode(query, SUB_DELIMS + ':@/?', encoding)
    if fragment is not None:
        fragment = uriencode(fragment, SUB_DELIMS + ':@/?', encoding)
    return uriunsplit((scheme, authority, path, query, fragment))
