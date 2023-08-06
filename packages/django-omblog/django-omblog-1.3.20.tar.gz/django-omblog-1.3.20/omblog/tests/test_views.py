from os import unlink
from PIL import Image
from unittest import skipIf

from django import VERSION
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from omblog.models import (
    Post,
    PostImage,
    Tag)

DJANGO_MINOR = VERSION[1]


class ViewTestCases(TestCase):

    def setUp(self):
        # make a post and attachment
        self.post = Post()
        self.post.title = 'Blog Post'
        self.post.slug = 'blog-post'
        self.post.source_content = 'Blog Post'
        self.post.status = Post.PUBLISHED
        self.post.save()

        # now user for the auth'd views
        self.user = User()
        self.user.username = 'test'
        self.user.set_password('test')
        self.user.email = 'test@test.com'
        self.user.is_active = True
        self.user.save()

    def test_multiple_tags(self):
        """Multiple tags don't cause 500 on views"""
        # make tags
        t1 = Tag(slug='a')
        t1.save()
        t2 = Tag(slug='a')
        t2.save()

        # get view and it is 200
        r = self.client.get(reverse('omblog:tag', args=[t2.slug]))
        self.assertEqual(200, r.status_code)

    def test_feed(self):
        """The feed view works as expected"""
        r = self.client.get(reverse('omblog:feed'))
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        """The login view works as expected"""
        # get is a 200
        r = self.client.get(reverse('omblog:login'))
        self.assertEqual(r.status_code, 200)

        # post is a 200
        r = self.client.post(reverse('omblog:login'), {})
        self.assertEqual(r.status_code, 200)

    def test_attach_delete_requires_login(self):
        """attach_delete requires login to access"""
        # attach delete is a 302
        r = self.client.post(reverse('omblog:attach_delete'), {})
        self.assertEqual(302, r.status_code)

    def test_attach_delete(self):
        """Attach delete works as expected"""
        # create image
        image = PostImage(post=self.post)
        image.title = 'Blog Post Image'
        image.src = 'fake/path/a.png'
        image.save()

        # login
        self.assertTrue(
            self.client.login(username='test', password='test'))

        # we have one post Image
        self.assertEqual(1, PostImage.objects.count())

        # post is a 200
        r = self.client.post(
            reverse('omblog:attach_delete'),
            {'pk': image.pk})
        self.assertEqual(200, r.status_code)

        # we have no post Images
        self.assertEqual(0, PostImage.objects.count())

        # Django 1.4 raises Http404 so just ignore these
        if DJANGO_MINOR > 4:
            # do a non existant one and we nicely 404
            r = self.client.post(
                reverse('omblog:attach_delete'),
                {'pk': 1230})
            self.assertEqual(404, r.status_code)

            # send junk and it fails nicely 404
            r = self.client.post(
                reverse('omblog:attach_delete'),
                {'pk': None})
            self.assertEqual(404, r.status_code)

    def test_attach_requires_login(self):
        """attach requires login to access"""
        r = self.client.post(reverse('omblog:attach'), {})
        self.assertEqual(302, r.status_code)

    def test_attach(self):
        """attach works as expected"""
        # login
        self.assertTrue(
            self.client.login(username='test', password='test'))

        # prep the data
        i = Image.new('RGB', (800, 800))
        i.save('omblog-test.jpg', 'JPEG')

        # send data
        with open('omblog-test.jpg') as fp:
            r = self.client.post(
                reverse('omblog:attach'),
                {'post': self.post.pk,
                 'phile': fp})
            self.assertEqual(200, r.status_code)

        # cleanup the file
        unlink('omblog-test.jpg')

        # Django 1.4 raises Http404 so just ignore these
        if DJANGO_MINOR > 4:
            # send junk for post and we get 404
            r = self.client.post(
                reverse('omblog:attach'),
                {'post': 12321321})
            self.assertEqual(404, r.status_code)

    def test_create_requires_login(self):
        """create requires login to access"""
        r = self.client.post(reverse('omblog:create'), {})
        self.assertEqual(302, r.status_code)

    def test_create_works_as_expected(self):
        """create creates!"""
        self.assertTrue(
            self.client.login(username='test', password='test'))

        # send garbage and we still have one
        # we got a 200
        r = self.client.post(reverse('omblog:create'), {
            'title': '',
            'description': '',
        })

        # we have one post
        self.assertEqual(1, Post.objects.count())

        # we got a 200
        r = self.client.post(reverse('omblog:create'), {
            'title': 'the title',
            'description': 'the description',
        })
        self.assertEqual(200, r.status_code)

        # we have two posts
        self.assertEqual(2, Post.objects.count())

    def test_edit_requires_login(self):
        """edit requires login to access"""
        r = self.client.get(reverse('omblog:edit', args=[self.post.pk]))
        self.assertEqual(302, r.status_code)

    @skipIf(
        DJANGO_MINOR <= 4,
        'Skipping test as Django version is 1.4 or less')
    def test_edit_works_as_expected(self):
        """edit edits!"""
        self.assertTrue(
            self.client.login(username='test', password='test'))

        # we got a 200 on GET
        r = self.client.get(reverse('omblog:edit', args=[self.post.pk]))
        self.assertEqual(200, r.status_code)

        # we got a 200 on POST
        data = {
            'title': 'The title',
            'status': 4,
            'slug': 'the-new-slug',
            'description': 'The description',
            'source_content': 'The content'}
        r = self.client.post(
            reverse('omblog:edit', args=[self.post.pk]),
            data)
        self.assertEqual(200, r.status_code)

        # everything was saved
        p = Post.objects.get(pk=self.post.pk)
        self.assertEqual(p.title, 'The title')
        self.assertEqual(p.description, 'The description')
        self.assertEqual(p.status, 4)
        self.assertEqual(p.slug, 'the-new-slug')
        self.assertEqual(p.source_content, 'The content')

    def test_tag(self):
        """tag yields 200"""
        # make tag and we get a 200
        tag = Tag(slug='t')
        tag.save()
        r = self.client.get(reverse('omblog:tag', args=[tag.slug]))
        self.assertEqual(200, r.status_code)

    def test_index(self):
        """index yields 200"""
        r = self.client.get(reverse('omblog:index'))
        self.assertEqual(200, r.status_code)

    def test_month(self):
        """month yields 200"""
        r = self.client.get(
            reverse('omblog:month', args=[
                self.post.created.year,
                self.post.created.month]))
        self.assertEqual(200, r.status_code)

    def test_post(self):
        """post yields 200"""
        r = self.client.get(reverse('omblog:post', args=[self.post.slug]))
        self.assertEqual(200, r.status_code)

    def test_post_404(self):
        """non existant post is 404"""
        # Django 1.4 raises Http404 so just ignore these
        if DJANGO_MINOR > 4:
            r = self.client.get(reverse('omblog:post', args=['shoes']))
            self.assertEqual(404, r.status_code)

    def test_redirect_edit_requires_login(self):
        """redirect_edit yields 302"""
        r = self.client.get(
            reverse('omblog:edit_redirect', args=[self.post.slug]))

        url = '{}?next=/blog/{}/edit/'.format(
            reverse('omblog:login'),
            self.post.slug)

        self.assertRedirects(r, url)

    @skipIf(
        DJANGO_MINOR <= 4,
        'Skipping test as Django version is 1.4 or less')
    def test_redirect_edit_redirects_when_logged_in(self):
        """redirect_edit redirects correctly"""
        self.assertTrue(
            self.client.login(username='test', password='test'))

        r = self.client.get(
            reverse('omblog:edit_redirect', args=[self.post.slug]))

        self.assertRedirects(r, reverse('omblog:edit', args=[self.post.pk]))
