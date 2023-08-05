from django.test import TestCase
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login

from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import loginView
from ftp_deploy.server.views import LogView
from ftp_deploy.tests.utils.factories import AdminUserFactory
from ftp_deploy.tests.utils.factories import LogFactory
from ftp_deploy.tests.utils.factories import ServiceFactory

from ftp_deploy.models import Log
from ftp_deploy.models import Service


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = AdminUserFactory()

    def test_login_page_render_login_template(self):
        """login page render login.html template"""
        request = RequestFactory().get(reverse('ftpdeploy_login'))
        view = setup_view(loginView(), request)
        self.assertEqual(view.template_name, 'ftp_deploy/login/login.html')

    def test_login_page_response(self):
        """login page response code 200"""
        response = self.client.get(reverse('ftpdeploy_login'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_success_login(self):
        """redirection after success login"""
        response = self.client.post(reverse('ftpdeploy_login'), {'username': 'admin', 'password': 'admin'})
        self.assertRedirects(response, reverse('ftpdeploy_dashboard'))

    def test_login_page_fail_login(self):
        """redirection for failed login attempt"""
        response = self.client.post(reverse('ftpdeploy_login'), {'username': 'admin_', 'password': 'admin_'})
        self.assertRedirects(response, reverse('ftpdeploy_login'))

    def test_login_page_already_login(self):
        """redirection from ogin screen for already login user"""
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('ftpdeploy_login'))
        self.assertRedirects(response, reverse('ftpdeploy_dashboard'))


class LogoutViewTest(TestCase):

    def test_logout_redirect(self):
        """Logout redirect to login page"""
        AdminUserFactory()
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('ftpdeploy_logout'))
        self.assertRedirects(response, reverse('ftpdeploy_login'))


class LogViewTest(TestCase):

    def setUp(self):
        request = RequestFactory().get(reverse('ftpdeploy_log'))
        self.view = setup_view(LogView(), request)

    def authenticate_user(self):
        AdminUserFactory()
        self.client.login(username='admin', password='admin')

    def test_log_page_response(self):
        """log page response code 200"""
        self.authenticate_user()
        response = self.client.get(reverse('ftpdeploy_log'))
        self.assertEqual(response.status_code, 200)

    def test_log_page_render_log_template(self):
        """log page render log.html template"""
        self.assertEqual(self.view.template_name, 'ftp_deploy/log/log.html')

    def test_log_page_process_log_model(self):
        """log view use Log model"""
        self.assertEqual(self.view.model, Log)

    def test_log_page_context_contain_service_list(self):
        """log page context contain service_list"""

        service1 = ServiceFactory.build()
        service1.check = False
        service1.save()
        service2 = ServiceFactory.build()
        service2.check = False
        service2.save()

        self.view.object_list = list()
        context = self.view.get_context_data()

        self.assertIn({'pk': service1.pk, 'repo_name': service1.repo_name}, context['service_list'])
        self.assertIn({'pk': service2.pk, 'repo_name': service2.repo_name}, context['service_list'])

    def test_log_post_request_response(self):
        """log post request response status code 200"""
        self.authenticate_user()
        response = self.client.post(reverse('ftpdeploy_log'), {'services': 0, 'status': 0})
        self.assertEqual(response.status_code, 200)

    def test_log_page_post_return_log_list_template(self):
        """Test log page post request return rentered log list template"""
        self.authenticate_user()
        response = self.client.post(reverse('ftpdeploy_log'), {'services': 0, 'status': 0})
        self.assertTemplateUsed(response, 'ftp_deploy/log/list.html')

    def test_log_page_post_filter(self):
        """Test log page post request return filtered services"""
        self.authenticate_user()
        service1 = ServiceFactory.build()
        service1.check = False
        service1.save()

        service2 = ServiceFactory.build()
        service2.check = False
        service2.save()

        log1 = LogFactory(service=service1)
        log2 = LogFactory(service=service2, status=False)

        response = self.client.post(reverse('ftpdeploy_log'), {'services': service1.pk, 'status': 1})
        self.assertListEqual(list(response.context['logs']), [log1,])

        response = self.client.post(reverse('ftpdeploy_log'), {'services': service1.pk, 'status': 0})
        self.assertListEqual(list(response.context['logs']), [])

        response = self.client.post(reverse('ftpdeploy_log'), {'services': service2.pk, 'status': 0})
        self.assertListEqual(list(response.context['logs']), [log2,])

        
