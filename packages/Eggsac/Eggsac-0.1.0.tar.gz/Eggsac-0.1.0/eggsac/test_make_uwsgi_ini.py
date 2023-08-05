#!/usr/bin/env python

import sys
import unittest

import make_uwsgi_ini

class Args(object):
    """Dummy args object"""

class ParseAddHeadersTests(unittest.TestCase):
    def test_parse(self):
        args = make_uwsgi_ini.parse_add_headers(
            Args(),
            """[["/output/", "'Access-Control-Allow-Origin' '*'"]]"""
        )
        self.assertIn(
            "add_header 'Access-Control-Allow-Origin' '*';",
            args.output_add_headers)
        self.assertFalse(args.slash_add_headers)

    def test_parse2(self):
        args = make_uwsgi_ini.parse_add_headers(
            Args(),
            """[\
["/output/", "'Access-Control-Allow-Origin' '*'"],\
["/output/", "'Foo-Bar' 'four-score years ago'"]\
]""")
        self.assertIn(
            "add_header 'Access-Control-Allow-Origin' '*';",
            args.output_add_headers)
        self.assertIn(
            "add_header 'Foo-Bar' 'four-score years ago';",
            args.output_add_headers)
#       print >>sys.stderr, "\n\n", args.output_add_headers
        self.assertEqual(2, len(args.output_add_headers.split('\n')))
        self.assertFalse(args.slash_add_headers)

    def test_parse_empty(self):
        args = make_uwsgi_ini.parse_add_headers(Args(), "")
        self.assertFalse(args.output_add_headers)
        self.assertFalse(args.slash_add_headers)
