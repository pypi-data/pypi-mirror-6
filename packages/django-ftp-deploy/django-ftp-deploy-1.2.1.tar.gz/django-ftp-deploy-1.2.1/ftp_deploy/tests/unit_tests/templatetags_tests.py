from django.test import TestCase
from django.test.client import RequestFactory
from django.template import Template
from django.template import Context
from django.template.context import RequestContext
from django.core.urlresolvers import reverse

from ftp_deploy.server.templatetags.active_tag import active


class ActiveTagTest(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()

    def test_template_math(self):
        """active template tag return active string if match url"""
        request = self.request_factory.get('/example')
        output = Template(
            "{% load active_tag %}"
            "{% active 'example' %}"

        ).render(RequestContext(request))

        self.assertEqual(output, 'active')

    def test_template_not_math(self):
        """active template tag return empty string if doesn't match url"""
        request = self.request_factory.get('/example')
        output = Template(
            "{% load active_tag %}"
            "{% active 'example_' %}"

        ).render(RequestContext(request))

        self.assertNotEqual(output, 'active')
