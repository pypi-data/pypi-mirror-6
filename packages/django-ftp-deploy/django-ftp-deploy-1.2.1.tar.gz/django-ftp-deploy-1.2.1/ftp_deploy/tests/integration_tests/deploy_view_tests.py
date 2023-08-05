from ftplib import FTP
import StringIO

from django.conf import settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call

from ftp_deploy.utils.ftp import ftp_connection
from ftp_deploy.models import Service
from ftp_deploy.tests.utils.factories import ServiceFactory
from ftp_deploy.tests.utils.payloads import LoadBitBucketPayload


class DeployViewTest(TestCase):

    def setUp(self):

        self.client = Client()
        self.payload = LoadBitBucketPayload()
        self.service = ServiceFactory()
        self.service_ftp = ServiceFactory(
            ftp_host=settings.FTP_TEST_SETTINGS['host'],
            ftp_username=settings.FTP_TEST_SETTINGS['username'],
            ftp_password=settings.FTP_TEST_SETTINGS['password'],
            ftp_path=settings.FTP_TEST_SETTINGS['path']
        )

    def ftp_connection(self):
        ftp = FTP(settings.FTP_TEST_SETTINGS['host'])
        ftp.login(settings.FTP_TEST_SETTINGS['username'], settings.FTP_TEST_SETTINGS['password'])
        ftp.cwd(settings.FTP_TEST_SETTINGS['path'])
        return ftp

    def ftp_read_file(self, ftp, file_path):
        io = StringIO.StringIO()
        ftp.retrbinary("RETR %s" % file_path, callback=lambda data: io.write(data))
        io.seek(0)
        return io.read()

    def test_deploy_view_wrong_branch(self):
        """deploy view with wrong branch return status code 200 with no action"""
        service = ServiceFactory(repo_branch='wrong_branch')
        payload = self.payload.payload_empty()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': service.secret_key}), {'payload': payload})
        self.assertEqual(response.status_code, 200)

    def test_deploy_view_ftp_fail(self):
        """deploy view with fail ftp data capture payload, set service status to Fail and return status code 500"""

        payload = self.payload.payload_empty()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service.secret_key}), {'payload': payload})
        service = Service.objects.get(pk=self.service.pk)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(service.log_set.all()[0].user, 'FTP Connection')
        self.assertFalse(service.log_set.all()[0].status)
        self.assertFalse(service.lock)
        self.assertFalse(service.status)

        self.assertIn('Log', service.status_message)
        self.assertIn('FTP', service.status_message)

    def test_deploy_view_curl_connection(self):
        """deploy view pass curl authenticate"""
        payload = self.payload.payload_empty()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_ftp.secret_key}), {'payload': payload})
        service = Service.objects.get(pk=self.service_ftp.pk)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(service.log_set.all()[0].status)
        self.assertEqual(service.log_set.all()[0].user, 'username')

        self.assertIn("<b>Bitbucket:</b> Repository %s doesn't exist" % self.service_ftp.repo_name, service.status_message)
        self.assertIn("<b>Bitbucket:</b> Hook is not set up", service.status_message)

    @patch('ftp_deploy.views.curl_connection')
    def test_deploy_view_ftp_transfer_data(self, mock_curl_connection):
        """deploy view transfer data from bitbucket to ftp"""
        ftp = self.ftp_connection()
        mock_curl = MagicMock(name='curl')
        mock_curl_connection.return_value = mock_curl

        mock_curl.perform = MagicMock(name='curl_perform_added', side_effect=['content added file1', 'content added file2', 'content added file3'])
        payload = self.payload.payload_added()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_ftp.secret_key}), {'payload': payload})
        service = Service.objects.get(pk=self.service_ftp.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(service.log_set.all()[0].status)
        self.assertEqual(self.ftp_read_file(ftp, 'file1.txt'), 'content added file1')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/file2.txt'), 'content added file2')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/folder2/folder3/file3.txt'), 'content added file3')
        mock_curl.assert_has_calls([call.authenticate(), call.close()])
        calls = ([call('https://api.bitbucket.org/1.0/repositories/username/service/raw/57baa5c89dae/file1.txt'),
                  call('https://api.bitbucket.org/1.0/repositories/username/service/raw/57baa5c89dae/folder1/file2.txt'),
                  call('https://api.bitbucket.org/1.0/repositories/username/service/raw/57baa5c89dae/folder1/folder2/folder3/file3.txt')])
        mock_curl.perform.assert_has_calls(calls)

        mock_curl.perform = MagicMock(name='curl_perform_modified', side_effect=['content modified file1', 'content modified file3'])
        payload = self.payload.payload_modified()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_ftp.secret_key}), {'payload': payload})
        service = Service.objects.get(pk=self.service_ftp.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(service.log_set.all()[1].status)
        self.assertEqual(self.ftp_read_file(ftp, 'file1.txt'), 'content modified file1')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/folder2/folder3/file3.txt'), 'content modified file3')

        payload = self.payload.payload_removed1()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_ftp.secret_key}), {'payload': payload})
        service = Service.objects.get(pk=self.service_ftp.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(service.log_set.all()[2].status)
        self.assertNotIn('folder2', ftp.nlst('folder1'))

        payload = self.payload.payload_removed2()
        response = self.client.post(reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service_ftp.secret_key}), {'payload': payload})
        service = Service.objects.get(pk=self.service_ftp.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(service.log_set.all()[3].status)
        self.assertNotIn('folder1', ftp.nlst())
        self.assertNotIn('file1.txt', ftp.nlst())

        ftp.quit()
