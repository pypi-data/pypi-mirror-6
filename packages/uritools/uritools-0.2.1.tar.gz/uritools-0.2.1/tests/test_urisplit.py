import unittest

from uritools import urisplit


class UriSplitTest(unittest.TestCase):

    def check(self, uri, parts):
        result = urisplit(uri)
        self.assertEqual(result, parts)
        for r, p in zip(result, parts):
            self.assertIsInstance(r, type(p))
        self.assertEqual(result.geturi(), uri)
        self.assertIsInstance(result.geturi(), type(uri))

    def test_rfc3986(self):
        """urisplit test cases from [RFC3986] 3. Syntax Components"""
        self.check(
            b'foo://example.com:8042/over/there?name=ferret#nose',
            (b'foo', b'example.com:8042', b'/over/there', b'name=ferret', b'nose')
        )
        self.check(
            u'foo://example.com:8042/over/there?name=ferret#nose',
            (u'foo', u'example.com:8042', u'/over/there', u'name=ferret', u'nose')
        )
        self.check(
            b'urn:example:animal:ferret:nose',
            (b'urn', None, b'example:animal:ferret:nose', None, None)
        )
        self.check(
            u'urn:example:animal:ferret:nose',
            (u'urn', None, u'example:animal:ferret:nose', None, None)
        )

    def test_abnormal(self):
        """urisplit edge cases"""
        for uri, parts in [
            ('', (None, None, '', None, None)),
            (':', (None, None, ':', None, None)),
            (':/', (None, None, ':/', None, None)),
            ('://', (None, None, '://', None, None)),
            ('://?', (None, None, '://', '', None)),
            ('://#', (None, None, '://', None, '')),
            ('://?#', (None, None, '://', '', '')),
            ('//', (None, '', '', None, None)),
            ('///', (None, '', '/', None, None)),
            ('//?', (None, '', '', '', None)),
            ('//#', (None, '', '', None, '')),
            ('//?#', (None, '', '', '', '')),
            ('?', (None, None, '', '', None)),
            ('??', (None, None, '', '?', None)),
            ('?#', (None, None, '', '', '')),
            ('#', (None, None, '', None, '')),
            ('##', (None, None, '', None, '#')),
        ]:
            self.check(uri, parts)

    def test_attributes(self):
        """urisplit attributes test cases"""

        uri = 'foo://user@example.com:8042/over/there?name=ferret#nose'
        result = urisplit(uri)
        self.assertEqual(result.scheme, 'foo')
        self.assertEqual(result.authority, 'user@example.com:8042')
        self.assertEqual(result.path, '/over/there')
        self.assertEqual(result.query, 'name=ferret')
        self.assertEqual(result.fragment, 'nose')
        self.assertEqual(result.userinfo, 'user')
        self.assertEqual(result.host, 'example.com')
        self.assertEqual(result.port, 8042)
        self.assertEqual(result.geturi(), uri)

        uri = 'urn:example:animal:ferret:nose'
        result = urisplit(uri)
        self.assertEqual(result.scheme, 'urn')
        self.assertEqual(result.authority, None)
        self.assertEqual(result.path, 'example:animal:ferret:nose')
        self.assertEqual(result.query, None)
        self.assertEqual(result.fragment, None)
        self.assertEqual(result.userinfo, None)
        self.assertEqual(result.host, None)
        self.assertEqual(result.port, None)
        self.assertEqual(result.geturi(), uri)
