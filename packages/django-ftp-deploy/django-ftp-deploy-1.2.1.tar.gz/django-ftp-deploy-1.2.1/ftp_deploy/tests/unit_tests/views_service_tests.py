from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call

from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import DashboardView
from ftp_deploy.server.views import ServiceManageView, ServiceAddView, ServiceEditView, ServiceDeleteView
from ftp_deploy.server.views import ServiceStatusView, ServiceNotificationView, ServiceRestoreView

from ftp_deploy.server.forms import ServiceNotificationForm, ServiceForm
from ftp_deploy.tests.utils.factories import AdminUserFactory, LogFactory, ServiceFactory
from ftp_deploy.models import Service


class ServiceDashboardViewTest(TestCase):

    def setUp(self):
        self.get_request = RequestFactory().get('/request')
        self.post_request = RequestFactory().post('/request', {'services': 0})

    def test_service_dashboard_view_render_dashboard_template(self):
        view = setup_view(DashboardView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/dashboard.html')

    def test_service_dashboard_view_set_services_in_appropriate_order(self):
        service1 = ServiceFactory()
        service2 = ServiceFactory(status=False)
        service3 = ServiceFactory()

        log1 = LogFactory(service=service1)
        log2 = LogFactory(service=service2)
        log3 = LogFactory(service=service3)

        view = setup_view(DashboardView(), self.get_request)
        response = view.get(view.request)
        object_list = list(response.context_data['object_list'])

        self.assertListEqual(object_list, [service2, service3, service1])

    def test_service_dashboard_view_display_services(self):
        service1 = ServiceFactory()
        service2 = ServiceFactory()

        view = setup_view(DashboardView(), self.get_request)
        response = view.get(view.request)

        self.assertContains(response, service1.repo_name)
        self.assertContains(response, service2.repo_name)

    def test_service_dashboard_view_POST_request_render_service_list_template(self):
        AdminUserFactory()
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('ftpdeploy_dashboard'), {'services': 0})

        self.assertTemplateUsed(response, 'ftp_deploy/service/list.html')

    def test_service_dashboard_view_POST_request_return_filtered_services(self):
        service1 = ServiceFactory(repo_name='repo_name1')
        service2 = ServiceFactory(repo_name='repo_name2')

        post_request = RequestFactory().post('/request', {'services': service1.pk})
        view = setup_view(DashboardView(), post_request)
        response = view.post(view.request)
        self.assertContains(response, service1.repo_name)
        self.assertNotContains(response, service2.repo_name)

        post_request = RequestFactory().post('/request', {'services': service2.pk})
        view = setup_view(DashboardView(), post_request)
        response = view.post(view.request)
        self.assertContains(response, service2.repo_name)
        self.assertNotContains(response, service1.repo_name)


class ServiceManageViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        self.get_request = RequestFactory().get('/request')
        self.post_request = RequestFactory().post('/request')

    def test_service_manage_view_render_service_manage_template(self):
        view = setup_view(ServiceManageView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/service/manage.html')


class ServiceAddViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        self.get_request = RequestFactory().get('/request')

    @patch('ftp_deploy.server.views.service.messages')
    def test_service_set_message_after_success_submit(self, mock_messages):
        mock_messages.add_message = MagicMock()
        view = setup_view(ServiceAddView(), self.get_request)
        view.object = MagicMock(name='object')
        view.get_success_url = MagicMock()

        view.form_valid(MagicMock(name='form'))

        self.assertTrue(mock_messages.add_message.called)

    def test_service_add_POST_request_perform_service_check(self):
        view = setup_view(ServiceAddView(), self.get_request)
        view.object = MagicMock(spec_set=Service)
        view.object.pk = self.service.pk

        response = view.get_success_url()

        calls = [call.check(), call.save()]
        view.object.assert_has_calls(calls)

    def test_service_add_view_redirect_to_service_manage_page_after_success_submit(self):
        view = setup_view(ServiceAddView(), self.get_request)
        view.object = MagicMock(spec_set=Service)
        view.object.pk = self.service.pk
        redirect = view.get_success_url()

        self.assertEqual(redirect, reverse('ftpdeploy_service_manage', kwargs={'pk': self.service.pk}))


class ServiceEditViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        service = Service.objects.filter(pk=self.service.pk).values()
        self.get_request = RequestFactory().get('/request')
        self.post_request = RequestFactory().post('/request', service[0])

    def test_service_edit_view_render_service_form_template(self):
        view = setup_view(ServiceEditView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/service/form.html')

    def test_service_edit_view_use_ServiceForm_instance(self):
        view = setup_view(ServiceEditView(), self.get_request)
        self.assertEqual(view.form_class, ServiceForm)

    @patch('ftp_deploy.server.views.service.messages')
    def test_service_edit_POST_request_set_message_after_success_submit(self, mock_messages):
        view = setup_view(ServiceEditView(), self.post_request, pk=self.service.pk)
        view.get_object = lambda: MagicMock(name='service')
        response = view.post(view.request)

        self.assertTrue(mock_messages.add_message.called)

    @patch('ftp_deploy.server.views.service.messages')
    def test_service_edit_POST_request_perform_service_check(self, mock_messages):
        view = setup_view(ServiceEditView(), self.post_request, pk=self.service.pk)
        view.get_object = lambda: MagicMock(name='service')
        response = view.post(view.request)

        view.object.assert_has_calls([call.check(), call.save()])

    def test_service_edit_view_redirect_to_service_dashboard_page_after_success_submit(self):
        view = setup_view(ServiceEditView(), self.get_request, pk=self.service.pk)
        redirect = view.get_success_url()

        self.assertEqual(redirect, reverse('ftpdeploy_service_manage', kwargs={'pk': self.service.pk}))


class ServiceDeleteViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        self.get_request = RequestFactory().get('/request')

    def test_service_delete_render_service_delete_template(self):
        view = setup_view(ServiceDeleteView(), self.get_request, pk=self.service.pk)
        self.assertEqual(view.template_name, 'ftp_deploy/service/delete.html')

    def test_service_delete_refirect_to_service_dsahboard_page(self):
        view = setup_view(ServiceDeleteView(), self.get_request, pk=self.service.pk)
        self.assertEqual(view.success_url, reverse('ftpdeploy_dashboard'))

    @patch('ftp_deploy.server.views.service.messages')
    def test_service_delete_set_message_after_success_submit(self, mock_messages):
        """service delete page return message after delete"""
        mock_messages.add_message = MagicMock()
        view = setup_view(ServiceDeleteView(), self.get_request, pk=self.service.pk)
        view.delete(view.request)

        self.assertTrue(mock_messages.add_message.called)


class ServiceStatusViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        self.get_request = RequestFactory().get('/request')

    def test_service_satus_POST_request_perform_service_check(self):
        view = setup_view(ServiceStatusView(), self.get_request)
        service = MagicMock(name='service')
        view.get_object = MagicMock(name='get_object', return_value=service)

        try:
            view.post(self.get_request)
        except:
            pass

        calls = [call.check(), call.save()]
        service.assert_has_calls(calls)

    @patch('ftp_deploy.server.views.ServiceStatusView.get_object')
    def test_service_status_POST_list_response_render_service_list_template(self, mock_object):
        self.service.check = MagicMock()
        self.service.save = MagicMock()
        mock_object.return_value = self.service

        AdminUserFactory()
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('ftpdeploy_service_status', kwargs={'pk': self.service.pk}), {'response': 'list'})

        self.assertTemplateUsed(response, 'ftp_deploy/service/list.html')

    def test_service_status_POST_list_response_display_service(self):
        post_request = RequestFactory().post('/request', {'response': 'list'})
        view = setup_view(ServiceStatusView(), post_request)
        self.service.check = MagicMock()
        self.service.save = MagicMock()
        view.get_object = MagicMock(return_value=self.service)
        response = view.post(view.request)

        self.assertContains(response, self.service.repo_name)

    @patch('ftp_deploy.server.views.ServiceStatusView.get_object')
    def test_service_status_POST_manage_response_render_service_manage_template(self, mock_object):
        self.service.check = MagicMock()
        self.service.save = MagicMock()
        mock_object.return_value = self.service

        AdminUserFactory()
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('ftpdeploy_service_status', kwargs={'pk': self.service.pk}), {'response': 'manage'})

        self.assertTemplateUsed(response, 'ftp_deploy/service/manage.html')

    @patch.object(ServiceManageView, 'get_context_data')
    @patch('ftp_deploy.server.views.ServiceStatusView.get_object')
    def test_service_status_POST_manage_response_context_mirror_service_manage_context(self, mock_object, mock_manage_context):
        self.service.check = MagicMock()
        self.service.save = MagicMock()
        mock_object.return_value = self.service
        mock_manage_context.return_value = {'service': self.service, 'manage_context': True}

        AdminUserFactory()
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('ftpdeploy_service_status', kwargs={'pk': self.service.pk}), {'response': 'manage'})

        self.assertTrue(response.context['manage_context'])

    def test_service_status_POST_json_response_return_proper_json_data(self):
        post_request = RequestFactory().post('/request', {'response': 'json'})
        view = setup_view(ServiceStatusView(), post_request)
        self.service.check = MagicMock()
        self.service.save = MagicMock()
        self.service.updated = 'now'
        self.service.status_message = 'status message'
        view.get_object = MagicMock(return_value=self.service)
        response = view.post(view.request)

        self.assertEqual(response.content, '{"status": true, "updated": "now", "status_message": "status message"}')


class ServiceNotificationViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        self.get_request = RequestFactory().get('/request')
        self.post_request = RequestFactory().post('/request')

    @patch('ftp_deploy.server.views.service.messages')
    def test_service_notification_set_message_after_success_submit(self, mock_messages):
        mock_messages.add_message = MagicMock()
        view = setup_view(ServiceNotificationView(), self.get_request)
        view.get_success_url = lambda: ''
        request = view.form_valid(MagicMock(name='form'))

        self.assertTrue(mock_messages.add_message.called)

    def test_service_notification_view_redirect_after_success_submit(self):
        view = setup_view(ServiceNotificationView(), self.get_request, pk=self.service.pk)
        request = view.get_success_url()
        self.assertEqual(request, reverse('ftpdeploy_service_manage', kwargs={'pk': self.service.pk}))


class ServiceRestoreViewTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()
        self.get_request = RequestFactory().get('/request')
        self.post_request = RequestFactory().post('/request', {'payload': True})

    def test_service_restore_view_context(self):
        log1 = LogFactory(service=self.service, status=False)
        log2 = LogFactory(service=self.service, status=False)

        view = setup_view(ServiceRestoreView(), self.get_request, pk=self.service.pk)
        view.object = self.service
        context = view.get_context_data()

        self.assertEqual(context['files_added'], [u'example/file2.txt'])
        self.assertEqual(context['files_modified'], [u'example/file1.txt'])
        self.assertEqual(context['files_removed'], [u'example/file3.txt'])
        self.assertEqual(context['service'], self.service)
        self.assertEqual(context['commits_info'], [[u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871'], [
                         u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871']])
        self.assertEqual(
            context['payload'], '{"commits": [{"node": "57baa5c89dae", "files": [{"type": "modified", "file": "example/file1.txt"}, {"type": "added", "file": "example/file2.txt"}, {"type": "added", "file": "example/file4.txt"}], "raw_author": "Author <author@email.com>", "utctimestamp": "2013-01-01 00:00:36+00:00", "author": "username", "timestamp": "2013-01-01 00:00:00", "raw_node": "57baa5c89daef238c2043c7e866c2e997d681871", "parents": ["322d9c181661"], "branch": "master", "message": "test message commit 1", "revision": null, "size": -1}, {"node": "57baa5c89daa", "files": [{"type": "modified", "file": "example/file1.txt"}, {"type": "removed", "file": "example/file3.txt"}, {"type": "removed", "file": "example/file4.txt"}], "raw_author": "Author <author@email.com>", "utctimestamp": "2013-01-01 00:00:36+00:00", "author": "username", "timestamp": "2013-01-01 00:00:00", "raw_node": "57baa5c89daef238c2043c7e866c2e997d681876", "parents": ["322d9c181662"], "branch": "master", "message": "test message commit 2", "revision": null, "size": -1}, {"node": "57baa5c89dae", "files": [{"type": "modified", "file": "example/file1.txt"}, {"type": "added", "file": "example/file2.txt"}, {"type": "added", "file": "example/file4.txt"}], "raw_author": "Author <author@email.com>", "utctimestamp": "2013-01-01 00:00:36+00:00", "author": "username", "timestamp": "2013-01-01 00:00:00", "raw_node": "57baa5c89daef238c2043c7e866c2e997d681871", "parents": ["322d9c181661"], "branch": "master", "message": "test message commit 1", "revision": null, "size": -1}, {"node": "57baa5c89daa", "files": [{"type": "modified", "file": "example/file1.txt"}, {"type": "removed", "file": "example/file3.txt"}, {"type": "removed", "file": "example/file4.txt"}], "raw_author": "Author <author@email.com>", "utctimestamp": "2013-01-01 00:00:36+00:00", "author": "username", "timestamp": "2013-01-01 00:00:00", "raw_node": "57baa5c89daef238c2043c7e866c2e997d681876", "parents": ["322d9c181662"], "branch": "master", "message": "test message commit 2", "revision": null, "size": -1}], "canon_url": "https://bitbucket.org", "user": "Restore", "repository": {"website": "", "fork": false, "name": "Service", "scm": "git", "absolute_url": "/username/service/", "owner": "username", "slug": "repo_slug", "is_private": true}, "truncated": false}')

    @patch('ftp_deploy.server.views.service.ServiceRestoreView.get_object')
    def test_service_restore_POST_request_remove_logs_from_logs_tree_and_return_deploy_view(self, mock_object):
        view = setup_view(ServiceRestoreView(), self.post_request)
        logs_tree = MagicMock(name='logs_tree')
        logs_tree.secret_key = 'abc123'
        mock_object.return_value = logs_tree

        response = view.post(view.request)

        logs_tree.get_logs_tree.assert_has_calls([call.delete()])
        self.assertIn(reverse('ftpdeploy_deploy', kwargs={'secret_key': logs_tree.secret_key}), response.__str__())
