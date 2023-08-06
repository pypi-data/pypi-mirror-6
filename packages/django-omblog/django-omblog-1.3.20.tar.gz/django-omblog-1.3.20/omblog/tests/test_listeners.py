from datetime import datetime
from django.test import TestCase
from omblog.models import Post


class ListenerTestCases(TestCase):

    def test_slug_created(self):
        post = Post()
        post.title = 'Test'
        post.description = 'Test'
        post.save()
        # we now have a date
        self.assertEqual(post.slug, 'test')

    def test_date_if_blank(self):
        """If no date is supplied for a post then
        datetime.now() is applied"""
        post = Post()
        post.title = 'Test'
        post.slug = 'test'
        post.source_content = "#Hello"
        post.save()
        # we now have a date
        self.assertTrue(post.created)

    def test_use_date_if_supplied(self):
        """If a date is supplied at the time of creation
        then it will be used when saving"""
        post_date = datetime.now()
        post = Post()
        post.title = 'Test'
        post.slug = 'test'
        post.source_content = "#Hello"
        post.created = post_date
        post.save()
        # we now have a date
        self.assertEqual(post_date, post.created)

    def test_pygments(self):
        """Pygments works as expected"""
        post = Post()
        post.title = 'Test'
        post.slug = 'test'
        post.source_content = '# Hello \n\n <code lang="jibberish">boom</code>'
        post.save()
        self.assertHTMLEqual(
            """<h1 id="hello">
            Hello
            </h1><p>
            <div class="highlight">
            <pre>
            boom
            </pre>
            </div>""",
            post.rendered_content)

    def test_markdown_rendering(self):
        """The source is rendered into markdown on saving"""
        post = Post()
        post.title = 'Test'
        post.slug = 'test'
        post.source_content = "# Hello"
        post.save()
        # we now have markdown
        self.assertHTMLEqual(
            '<h1 id="hello">Hello</h1>',
            post.rendered_content)
