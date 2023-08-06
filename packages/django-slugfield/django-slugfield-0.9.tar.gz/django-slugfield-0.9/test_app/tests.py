
import os
import sys

if __name__ == '__main__':
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=['test_app'],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
    )


parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, parent_dir)

from django.test import TestCase
from test_app.forms import ArticleModelForm, ArticleForm


class ModelFormTestCase(TestCase):

    def test_valid_slug(self):
        data = {
            'name': u'About testing',
            'slug': u'valid-slug',
            }
        form = ArticleModelForm(data)
        form_html = str(form)
        self.assertNotIn('class="errorlist"', form_html)
        self.assertIn('value="valid-slug"', form_html)

    def test_invalid_slug(self):
        data = {
            'name': u'About testing',
            'slug': u'invalid    slug',
            }
        form = ArticleModelForm(data)
        form_html = str(form)
        self.assertIn('class="errorlist"', form_html)
        self.assertIn('value="invalid    slug"', form_html)

    def test_empty_slug(self):
        data = {
            'name': u'About testing',
            'slug': u'',
            }
        form = ArticleModelForm(data)
        form_html = str(form)
        self.assertIn('class="errorlist"', form_html)
        self.assertIn('value="about-testing?"', form_html)


class FormTestCase(TestCase):

    def test_valid_slug(self):
        data = {
            'name': u'About testing',
            'slug': u'valid-slug',
            }
        form = ArticleForm(data)
        form_html = str(form)
        self.assertNotIn('class="errorlist"', form_html)
        self.assertIn('value="valid-slug"', form_html)

    def test_invalid_slug(self):
        data = {
            'name': u'About testing',
            'slug': u'invalid    slug',
            }
        form = ArticleForm(data)
        form_html = str(form)
        self.assertIn('class="errorlist"', form_html)
        self.assertIn('value="invalid    slug"', form_html)

    def test_empty_slug(self):
        data = {
            'name': u'About testing',
            'slug': u'',
            }
        form = ArticleForm(data)
        form_html = str(form)
        self.assertIn('class="errorlist"', form_html)
        self.assertIn('value="about-testing?"', form_html)


if __name__ == '__main__':
    from django.test.runner import DiscoverRunner

    test_runner = DiscoverRunner()
    failures = test_runner.run_tests(['test_app'])
    if failures:
        sys.exit(failures)
