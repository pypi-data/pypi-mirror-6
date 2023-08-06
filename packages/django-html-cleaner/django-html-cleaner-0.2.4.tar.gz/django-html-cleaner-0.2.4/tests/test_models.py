import unittest
from .models import Post


class TestHtmlcleaner(unittest.TestCase):

    def setUp(self):
        pass

    def test_none_field_does_not_explode(self):
        post = Post.objects.create(id=1,title="Hi")
        self.assert_(Post.objects.get(id=1))

    def test_blank_field_does_not_explode(self):
        post = Post.objects.create(id=1,title="Hi",body="")
        self.assert_(Post.objects.get(id=1))

    def test_char_field_works(self):
        body = """<p onclick="alert()">Hello world!</p>
                  <p>How are you?</p>
                  <script src="/scripts/whoa.js"></script>"""
        post = Post.objects.create(
            id=1,
            title="<b onclick='alert()'>Super</b> title",
            body=body)

        post = Post.objects.get(id=1)
        self.assertEqual("<span><b>Super</b> title</span>", post.title)

    def test_text_field_works(self):
        body = """<p onclick="alert()">Hello world!</p>
                  <p>How are you?</p>
                  <script src="/scripts/whoa.js"></script>"""
        post = Post.objects.create(
            id=1,
            title="<b onclick='alert()'>Super</b> title",
            body=body)
        expected = "<div><p>Hello world!</p><p>How are you?</p></div>"

        post = Post.objects.get(id=1)
        self.assertEqual(expected, post.body)

    def test_model_value_updated_on_save(self):
        body = """<p onclick="alert()">Hello world!</p>
                  <p>How are you?</p>
                  <script src="/scripts/whoa.js"></script>"""
        post = Post.objects.create(
            id=1,
            title="Super title",
            body=body)
        expected = "<div><p>Hello world!</p><p>How are you?</p></div>"

        # Note that unlike the tests above, we do not get the post back
        # from the DB.
        self.assertEqual(expected, post.body)

    def tearDown(self):
        Post.objects.all().delete()
