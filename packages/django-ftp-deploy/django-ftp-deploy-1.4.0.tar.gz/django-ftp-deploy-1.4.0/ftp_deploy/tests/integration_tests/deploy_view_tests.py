from ftplib import FTP
import StringIO
from mock import MagicMock, PropertyMock, patch, call

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse


from ftp_deploy.utils.ftp import ftp_connection
from ftp_deploy.models import Service
from ftp_deploy.tests.utils.factories import ServiceFactory, TaskFactory
from ftp_deploy.tests.utils.payloads import LoadPayload


class DeployViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.payload = LoadPayload()
        self.service_bb = ServiceFactory()
        self.service_gh = ServiceFactory(repo_source='gh')

    def test_deploy_view_wrong_secret_key_return_404(self):
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key':'wrong_secret_key'}))
        self.assertEqual(response.status_code, 404)

    @patch('ftp_deploy.views.deploy_task')
    def test_POST_request_perform_bb_deploy_task_and_return_status_200(self, mock_deploy_task):
        mock_deploy_task.apply_async = MagicMock(name='apply_async')

        payload = self.payload.bb_payload_empty()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_bb.secret_key}), {'payload': payload})
        self.assertTrue(mock_deploy_task.apply_async.called)
        self.assertEqual(response.status_code, 200)

    @patch('ftp_deploy.views.deploy_task')
    def test_POST_request_perform_gh_deploy_task_and_return_status_200(self, mock_deploy_task):
        mock_deploy_task.apply_async = MagicMock(name='apply_async')

        payload = self.payload.gh_payload_empty()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_gh.secret_key}), {'payload': payload})
        self.assertTrue(mock_deploy_task.apply_async.called)
        self.assertEqual(response.status_code, 200)

    def test_POST_request_create_task(self):
        payload = self.payload.bb_payload_empty()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_bb.secret_key}), {'payload': payload})
        self.assertTrue(self.service_bb.task_set.all().exists())


class DeployStatusViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.service = ServiceFactory()

    def test_service_without_queue_return_count_0(self):
        response = self.client.post(reverse('ftpdeploy_deploy_status', kwargs={'secret_key': self.service.secret_key}))
        self.assertEqual(response.content,'{"queue": 0}')

    @patch('ftp_deploy.views.AsyncResult')    
    def test_service_status_with_queue_call_async_result_and_return_json(self, mock_async_result):
        task = TaskFactory(service=self.service)
        result =  MagicMock(name='results',result=dict(result=22,file='file1.txt'), return_value=22)
        mock_async_result.return_value = result
        response = self.client.post(reverse('ftpdeploy_deploy_status', kwargs={'secret_key': self.service.secret_key}))

        mock_async_result.has_calls([call(u'factory_name_1')])
        self.assertEqual(response.content,'{"queue": 1, "result": 22, "file": "file1.txt"}')

