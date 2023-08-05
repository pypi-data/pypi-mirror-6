from django.test import TestCase
from django.core.urlresolvers import reverse

from ftp_deploy.server.forms import LoginForm, NotificationForm, ServiceForm, ServiceNotificationForm
from ftp_deploy.tests.utils.factories import AdminUserFactory, ServiceFactory


class LoginFormTest(TestCase):

    def test_login_form_required_fiels(self):
        """login form requirements for pass validation"""
        form_data = {
            'username': '',
            'password': ''
        }

        form = LoginForm(form_data)

        self.assertFalse(form.is_valid())

        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)

        form_data = {
            'username': 'data',
            'password': 'data'
        }

        form = LoginForm(form_data)
        self.assertTrue(form.is_valid())


class NotificationFormTest(TestCase):

    def test_notification_form_required_fiels(self):
        """norification requirements to pass validation """
        form = NotificationForm({})
        self.assertFalse(form.is_valid())

        form_data = {
            'name': 'name',
        }

        form = NotificationForm(form_data)
        self.assertTrue(form.is_valid())


class ServiceFormTest(TestCase):

    def test_service_form_required_fiels(self):
        """service form require number of fields to pass validation"""
        form = ServiceForm({})
        self.assertFalse(form.is_valid())

        self.assertIn('ftp_username', form.errors)
        self.assertIn('ftp_host', form.errors)
        self.assertIn('ftp_password', form.errors)
        self.assertIn('ftp_path', form.errors)
        self.assertIn('repo_name', form.errors)
        self.assertIn('repo_source', form.errors)
        self.assertIn('repo_slug_name', form.errors)
        self.assertIn('repo_branch', form.errors)
        self.assertIn('secret_key', form.errors)


class ServiceNotificationFormTest(TestCase):

    def test_service_notification_form_required_fiels(self):

        form = ServiceNotificationForm({})
        self.assertTrue(form.is_valid())
