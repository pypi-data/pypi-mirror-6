import sys

pyver = sys.version_info[0]

__all__ = [
    'pyver', 'unicode_type', 'encoded_type', 'range_iterator', 'HTMLParser', 'unquote_plus'
]

if pyver == 2:
    unicode_type = unicode
    encoded_type = str
    range_iterator = xrange
    import HTMLParser
    from urllib import unquote_plus
elif pyver == 3:
    unicode_type = str
    encoded_type = bytes
    range_iterator = range
    import html.parser as HTMLParser
    from urllib.parse import unquote_plus
