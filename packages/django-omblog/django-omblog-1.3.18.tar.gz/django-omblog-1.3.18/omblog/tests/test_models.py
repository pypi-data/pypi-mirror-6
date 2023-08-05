from django.test import TestCase
from omblog.models import Post


class ModelTestCases(TestCase):

    def test_edit_url(self):
        """edit url returns correctly"""
        p = Post()
        p.title = 'This is a test post'
        p.slug = 'this-is-test-post'
        p.source_content = 'Hm, ha ha.'
        p.save()
        self.assertEqual(p.edit_url(), '/blog/edit/1/')
