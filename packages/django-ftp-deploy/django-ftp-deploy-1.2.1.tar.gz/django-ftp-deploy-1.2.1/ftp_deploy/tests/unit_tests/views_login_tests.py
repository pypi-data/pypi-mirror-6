from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call

from ftp_deploy.conf import *
from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import loginView, logoutView
from ftp_deploy.server.forms import LoginForm


class LoginViewTest(TestCase):

    def setUp(self):
        self.get_request = RequestFactory().get('/request')

    def test_login_view_user_proper_form_instance(self):
        view = setup_view(loginView(), self.get_request)
        self.assertEqual(view.form_class, LoginForm, "Login form is not instance of LoginForm")

    def test_login_view_render_proper_template(self):
        view = setup_view(loginView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/login/login.html', "login page use wrong template")

    def test_login_view_status_code(self):
        view = setup_view(loginView(), self.get_request)
        view.request.user = MagicMock()
        view.request.user.is_authenticated = MagicMock(name='is_authenticated', return_value=False)
        response = view.get(view.request)
        self.assertEqual(response.status_code, 200)

    def test_login_view_redirect_if_already_login(self):
        view = setup_view(loginView(), self.get_request)
        view.request.user = MagicMock(name='user')
        view.request.user.is_authenticated = MagicMock(name='is_authenticated', return_value=True)
        response = view.get(view.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('ftpdeploy_dashboard'), response.__str__())

    @patch('ftp_deploy.server.views.login.messages')
    @patch('ftp_deploy.server.views.login.authenticate')
    def test_form_valid_authenticate_fail_set_error_message(self, mock_authenticate, mock_messages):
        mock_messages.error = MagicMock(name='error_message')
        mock_authenticate.return_value = None

        view = setup_view(loginView(), self.get_request)
        view.form_class = MagicMock()
        response = view.form_valid(view.form_class)

        mock_messages.error.assert_has_calls
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('ftpdeploy_login'), response.__str__())

    @patch('ftp_deploy.server.views.login.login_user')
    @patch('ftp_deploy.server.views.login.authenticate')
    def test_form_valid_authenticate_success_log_user_in(self, mock_authenticate, mock_login_user):
        mock_authenticate.return_value = True
        self.get_request.session = MagicMock(name='session')

        view = setup_view(loginView(), self.get_request)
        view.form_class = MagicMock(name='form')
        view.form_class.cleaned_data.__getitem__ = MagicMock(name='cleaned_data', return_value='admin')
        get_request = view.form_valid(view.form_class)

        mock_authenticate.assert_called_once_with(username='admin', password='admin')
        mock_login_user.assert_has_calls


class LogoutViewTest(TestCase):

    def setUp(self):
        self.get_request = RequestFactory().get('/request')

    @patch('ftp_deploy.server.views.login.logout')
    def test_logout_view_call_logout_method(self, mock_logout):
        view = setup_view(logoutView(), self.get_request)
        view.get(view.request)
        mock_logout.assert_called_once_with(view.request)

    def test_logout_redirect_to_login_page(self):
        self.get_request.session = MagicMock()
        view = setup_view(logoutView(), self.get_request)
        response = view.get(view.request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('ftpdeploy_login'), response.__str__())
