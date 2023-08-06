import unittest

from lxml.html import fromstring, tostring
from django_html_cleaner.cleaner import Cleaner


def normalize(html):
    return tostring(fromstring(html), encoding="utf-8")

n = normalize


class TestCleaner(unittest.TestCase):

    def setUp(self):
        pass

    def test_cleaner_with_no_args_removes_js(self):
        cleaner = Cleaner()
        html = """<p onclick="alert()">Hello world!</p>
                  <p>How are you?</p>
                  <script src="/scripts/whoa.js"></script>"""
        expected = "<div><p>Hello world!</p><p>How are you?</p></div>"
        cleaned_html = cleaner.clean(html)
        self.assertEqual(cleaned_html, expected)

    def test_cleaner_with_no_args_allows_styles(self):
        cleaner = Cleaner()
        html = """<p style="font-weight: bold; color: #333;">Hi there!</p>"""
        expected = html
        self.assertEqual(expected, cleaner.clean(html))

    def test_cleaner_can_eliminate_styles(self):
        cleaner = Cleaner(allowed_styles=['font-weight', 'text-decoration'])
        html = """<p style="font-weight: bold; color: #333;">Hi there!</p>"""
        expected = """<p style="font-weight: bold;">Hi there!</p>"""
        self.assertEqual(expected, cleaner.clean(html))

    def test_cleaner_can_eliminate_specific_tags(self):
        cleaner = Cleaner(allowed_tags=['p', 'strong', 'em'])
        html = """<p onclick="alert()"><strong>Hello world!</strong></p>
                  <p class="fool"><blink>How <tt>are</tt> you?</blink></p>
                  <script src="/scripts/whoa.js"></script>"""
        expected = """<div><p><strong>Hello world!</strong></p>""" \
            """<p class="fool">How are you?</p></div>"""
        self.assertEqual(expected, cleaner.clean(html))

    def test_cleaner_can_eliminate_specific_attributes(self):
        cleaner = Cleaner(allowed_attributes=['class'])
        html = """<p id="what-up" class="fool">How <tt>are</tt> you?</p>"""
        expected = """<p class="fool">How <tt>are</tt> you?</p>"""
        self.assertEqual(expected, cleaner.clean(html))

    def test_cleaner_can_wrap_in_specific_parent_tag(self):
        cleaner = Cleaner(create_parent="section")
        html = """<p onclick="alert()">Hello world!</p>
                  <p>How are you?</p>
                  <script src="/scripts/whoa.js"></script>"""
        expected = "<section><p>Hello world!</p><p>How are you?</p></section>"
        self.assertEqual(expected, cleaner.clean(html))

    def tearDown(self):
        pass
