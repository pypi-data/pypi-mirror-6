from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call

from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import LogView, LogSkipDeployView
from ftp_deploy.tests.utils.factories import AdminUserFactory, LogFactory, ServiceFactory
from ftp_deploy.models import Log


class LogViewTest(TestCase):

    def setUp(self):
        self.get_request = RequestFactory().get('/request')

    def test_log_page_render_proper_template(self):
        view = setup_view(LogView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/log/log.html')

    def test_log_display_logs_entries(self):
        log1 = LogFactory()
        log2 = LogFactory()
        view = setup_view(LogView(), self.get_request)
        response = view.get(view.request)

        self.assertContains(response, log1.service)
        self.assertContains(response, log2.service)

    def test_log_page_POST_request_render_log_list_template(self):
        AdminUserFactory()
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('ftpdeploy_log'), {'services': 0, 'status': 0})

        self.assertTemplateUsed(response, 'ftp_deploy/log/list.html')

    def test_log_page_POST_request_return_filtered_logs(self):
        service1 = ServiceFactory(repo_name='service_1')
        service2 = ServiceFactory(repo_name='service_2')
        service3 = ServiceFactory(repo_name='service_3')
        log1 = LogFactory(service=service1)
        log2 = LogFactory(service=service2)
        log3 = LogFactory(service=service3, status=False)

        post_request = RequestFactory().post('/request', {'services': 0, 'status': 0})
        view = setup_view(LogView(), post_request)
        response = view.post(view.request)
        self.assertContains(response, 'No Results')

        post_request = RequestFactory().post('/request', {'services': service1.pk, 'status': 1})
        view = setup_view(LogView(), post_request)
        response = view.post(view.request)
        self.assertContains(response, log1.service)
        self.assertNotContains(response, log3.service)

        post_request = RequestFactory().post('/request', {'services': service3.pk, 'status': 0})
        view = setup_view(LogView(), post_request)
        response = view.post(view.request)

        self.assertContains(response, log3.service)
        self.assertNotContains(response, log1.service)
        self.assertNotContains(response, log2.service)


class LogSkipDeployViewTest(TestCase):

    def setUp(self):
        self.post_request = RequestFactory().post('/request')

    def test_log_skip_deploy_view_POST_request_set_skip_flag(self):
        log1 = LogFactory()
        view = setup_view(LogSkipDeployView(), self.post_request)
        view.get_object = lambda: log1
        response = view.post(view.request)
        log = Log.objects.get(pk=log1.pk)

        self.assertTrue(log.skip)

    def test_log_skip_deploy_view_POST_request_return_json_response(self):
        log1 = LogFactory()
        view = setup_view(LogSkipDeployView(), self.post_request, pk=log1.pk)
        response = view.post(view.request)

        self.assertEqual('{"status": "success"}', response.content)
