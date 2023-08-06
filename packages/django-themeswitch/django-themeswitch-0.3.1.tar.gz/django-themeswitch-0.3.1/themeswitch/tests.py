"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import RequestFactory
from themeswitch.settings import THEMES
from themeswitch.context_processors import selected_theme


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_selected_theme(self):
        """
        Tests that "selected_theme" is added to context
        """
        request = self.factory.get('/')
        ctx = selected_theme(request)
        self.assertIn('selected_theme', ctx)

        self.assertNotIn('bogus', THEMES)
        self.factory.cookies['selected_theme'] = 'bogus'
        request = self.factory.get('/')
        ctx = selected_theme(request)
        self.assertIn('selected_theme', ctx)
        self.assertDictEqual(dict(selected_theme='foo'), ctx)

        self.assertIn('bar', THEMES)
        self.factory.cookies['selected_theme'] = 'bar'
        request = self.factory.get('/')
        ctx = selected_theme(request)
        self.assertDictEqual(dict(selected_theme='bar'), ctx)
