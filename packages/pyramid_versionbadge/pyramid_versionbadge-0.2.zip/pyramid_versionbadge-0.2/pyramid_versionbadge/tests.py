#coding:utf8

import unittest
from pyramid import testing
from webtest import TestApp

BODY = '<html><head></head><body></body></html>'


def view(request):
    response = request.response
    response.content_type = 'text/html'
    response.body = BODY
    return response


class Base(unittest.TestCase):

    def configure(self):
        self.config.registry.settings.update({})

    def setUp(self):
        self.config = testing.setUp()
        self.configure()
        self.config.include('pyramid_versionbadge')
        self.config.add_route('index', '/')
        self.config.add_view(route_name='index', view=view)
        self.app = TestApp(self.config.make_wsgi_app())

    def tearDown(self):
        testing.tearDown()


class TestTweenUnconfigured(Base):

    def test_badge_with_default_value_is_rendered(self):
        resp = self.app.get('/')
        resp.mustcontain('<div id="versionbadge" class="">BETA</div>')


class TestTweenConfigured(Base):

    def configure(self):
        self.config.registry.settings.update({'versionbadge.text': 'Boo',
                                     'versionbadge.css': 'bar'})

    def test_badge_with_set_values_is_rendered(self):
        resp = self.app.get('/')
        resp.mustcontain('<div id="versionbadge" class="bar">Boo</div>')

    def tearDown(self):
        testing.tearDown()


class TestTweenDeactivate(Base):

    def configure(self):
        self.config.registry.settings.update({'versionbadge.text': '',
                                     'versionbadge.css': 'bar'})

    def test_badge_with_text_set_to_emtpy_string_is_not_rendered(self):
        resp = self.app.get('/')
        assert resp.body == BODY

    def tearDown(self):
        testing.tearDown()

