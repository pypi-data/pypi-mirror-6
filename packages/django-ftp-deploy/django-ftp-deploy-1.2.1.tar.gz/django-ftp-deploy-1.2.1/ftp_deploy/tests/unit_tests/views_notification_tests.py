from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse


from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call

from ftp_deploy.conf import *
from ftp_deploy.tests.utils.cbv import setup_view
from ftp_deploy.server.views import NotificationView, NotificationAddView, NotificationEditView, NotificationDeleteView
from ftp_deploy.server.views import DashboardView


from ftp_deploy.server.forms import NotificationForm
from ftp_deploy.tests.utils.factories import NotificationFactory
from ftp_deploy.models import Log, Service, Notification


class NotificationViewTest(TestCase):

    def setUp(self):
        self.get_request = RequestFactory().get('/request')

    def test_notification_view_render_notification_template(self):
        view = setup_view(NotificationView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/notification/notification.html')

    def test_notification_view_display_notifications(self):
        notification1 = NotificationFactory()
        notification2 = NotificationFactory()

        view = setup_view(NotificationView(), self.get_request)
        response = view.get(view.request)

        self.assertContains(response, notification1.name)
        self.assertContains(response, notification2.name)


class NotificationAddViewTest(TestCase):

    def setUp(self):
        self.get_request = RequestFactory().get('/request')

    def test_notification_add_view_render_notification_form_template(self):
        view = setup_view(NotificationAddView(), self.get_request)
        self.assertEqual(view.template_name, 'ftp_deploy/notification/form.html')

    def test_notification_add_view_user_NotificationForm_instance(self):
        view = setup_view(NotificationAddView(), self.get_request)
        self.assertEqual(view.form_class, NotificationForm)

    def test_notification_add_view_redirect_to_notification_page_after_success_submit(self):
        view = setup_view(NotificationAddView(), self.get_request)
        self.assertEqual(view.success_url, reverse('ftpdeploy_notification'))

    @patch('ftp_deploy.server.views.notification.messages')
    def test_notification_add_view_set_message_after_success_submit(self, mock_messages):
        view = setup_view(NotificationAddView(), self.get_request)
        mock_messages.add_message = MagicMock()
        view.form_class = MagicMock()
        view.form_valid(view.form_class)
        self.assertTrue(mock_messages.add_message.called)


class NotificationEditViewTest(TestCase):

    def setUp(self):
        self.notification = NotificationFactory()
        self.get_request = RequestFactory().get('/request')

    def test_notification_edit_view_context_contain_email_list(self):
        view = setup_view(NotificationEditView(), self.get_request, pk=self.notification.pk)
        response = view.get(view.request)
        self.assertEqual(response.context_data['emails'], self.notification.get_email_list())

    @patch('ftp_deploy.server.views.notification.messages')
    def test_notification_edit_view_set_message_after_success_submit(self, mock_messages):
        view = setup_view(NotificationEditView(), self.get_request)
        mock_messages.add_message = MagicMock()
        view.form_class = MagicMock()
        view.form_valid(view.form_class)
        self.assertTrue(mock_messages.add_message.called)


class NotificationDeleteViewTest(TestCase):

    def setUp(self):
        self.notification = NotificationFactory()
        self.get_request = RequestFactory().get('/get')

    def test_notification_delete_view_redirect_to_notification_page(self):
        view = setup_view(NotificationDeleteView(), self.get_request, pk=self.notification.pk)
        self.assertEqual(view.success_url, reverse('ftpdeploy_notification'))

    def test_notification_delete_view_render_notification_delete_template(self):
        view = setup_view(NotificationDeleteView(), self.get_request, pk=self.notification.pk)
        self.assertEqual(view.template_name, 'ftp_deploy/notification/delete.html')

    @patch('ftp_deploy.server.views.notification.messages')
    def test_notification_delete_view_set_message_after_success_submit(self, mock_messages):
        """notification delete page return message after delete"""
        view = setup_view(NotificationDeleteView(), self.get_request, pk=self.notification.pk)
        mock_messages.add_message = MagicMock()
        view.delete(view.request)
        self.assertTrue(mock_messages.add_message.called)
