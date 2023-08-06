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
from ftp_deploy.utils.deploy import Deploy
from ftp_deploy.models import Service
from ftp_deploy.tests.utils.factories import ServiceFactory, TaskFactory
from ftp_deploy.tests.utils.payloads import LoadPayload


class DeployUtilsTest(TestCase):

    def setUp(self):

        self.client = Client()
        self.payload = LoadPayload()
        self.service_bb = ServiceFactory()
        self.service_gh = ServiceFactory(repo_source='gh')

        self.service_ftp_bb = ServiceFactory(
            ftp_host=settings.FTP_TEST_SETTINGS['host'],
            ftp_username=settings.FTP_TEST_SETTINGS['username'],
            ftp_password=settings.FTP_TEST_SETTINGS['password'],
            ftp_path=settings.FTP_TEST_SETTINGS['path']
        )
        self.service_ftp_gh = ServiceFactory(
            ftp_host=settings.FTP_TEST_SETTINGS['host'],
            ftp_username=settings.FTP_TEST_SETTINGS['username'],
            ftp_password=settings.FTP_TEST_SETTINGS['password'],
            ftp_path=settings.FTP_TEST_SETTINGS['path'],
            repo_source='gh'
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

    def test_deploy_ftp_fail(self):
        """deploy view with fail ftp data capture payload, set service status to Fail"""

        payload = self.payload.bb_payload_empty()
        task = TaskFactory(service=self.service_bb)
        deploy = Deploy('host', payload, self.service_bb, task.name)
        deploy.perform()

        service = Service.objects.get(pk=self.service_bb.pk)

        self.assertEqual(service.log_set.all()[0].user, 'FTP Connection')
        self.assertFalse(service.log_set.all()[0].status)
        self.assertFalse(service.lock())
        self.assertFalse(service.status)

        self.assertIn('Log', service.status_message)
        self.assertIn('FTP', service.status_message)

    def test_deploy_bitbucket_curl_connection(self):
        """deploy view pass bitbucket curl authenticate"""
        payload = self.payload.bb_payload_empty()
        task = TaskFactory(service=self.service_bb)
        deploy = Deploy('host', payload, self.service_ftp_bb, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_bb.pk)

        self.assertTrue(service.log_set.all()[0].status)
        self.assertEqual(service.log_set.all()[0].user, 'username')

        self.assertIn("<b>Bitbucket:</b> Repository %s doesn't exist" % self.service_ftp_bb.repo_name, service.status_message)
        self.assertIn("<b>Bitbucket:</b> Hook is not set up", service.status_message)

    def test_deploy_github_curl_connection(self):
        """deploy view pass github curl authenticate"""
        
        payload = self.payload.gh_payload_empty()
        task = TaskFactory(service=self.service_gh)
        deploy = Deploy('host', payload, self.service_ftp_gh, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_gh.pk)

        self.assertTrue(service.log_set.all()[0].status)
        self.assertEqual(service.log_set.all()[0].user, 'Pusher')

        self.assertIn("<b>Github:</b> Repository %s doesn't exist" % self.service_ftp_gh.repo_name, service.status_message)
        self.assertIn("<b>Github:</b> Hook is not set up", service.status_message)

    @patch('ftp_deploy.utils.deploy.current_task')
    @patch('ftp_deploy.utils.deploy.curl_connection')
    def test_deploy_view_ftp_transfer_bb_data(self, mock_curl_connection, mock_current_task):
        """deploy view transfer data from bitbucket to ftp"""
        ftp = self.ftp_connection()
        mock_curl = MagicMock(name='curl')
        mock_curl_connection.return_value = mock_curl

        mock_curl.perform = MagicMock(name='curl_perform_added', side_effect=['content added file1', 'content added file2', 'content added file3'])
        # test create files
        payload = self.payload.bb_payload_added()
        task = TaskFactory(service=self.service_bb)
        deploy = Deploy('host', payload, self.service_ftp_bb, task.name)
        deploy.perform()

        service = Service.objects.get(pk=self.service_ftp_bb.pk)
        self.assertTrue(service.log_set.all()[0].status)

            # test task is removed after success deploy
        self.assertFalse(service.task_set.all().exists())

        self.assertEqual(self.ftp_read_file(ftp, 'file1.txt'), 'content added file1')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/file2.txt'), 'content added file2')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/folder2/folder3/file3.txt'), 'content added file3')
        mock_curl.assert_has_calls([call.authenticate(), call.close()])
        calls = ([call('https://api.bitbucket.org/1.0/repositories/username/service/raw/57baa5c89dae/file1.txt'),
                  call('https://api.bitbucket.org/1.0/repositories/username/service/raw/57baa5c89dae/folder1/file2.txt'),
                  call('https://api.bitbucket.org/1.0/repositories/username/service/raw/57baa5c89dae/folder1/folder2/folder3/file3.txt')])

        # test celery update progress
        mock_current_task.assert_has_calls([call.update_state(state='PROGRESS', meta={'status': 0, 'file': u'file1.txt'}), call.update_state(
            state='PROGRESS', meta={'status': 33, 'file': u'file2.txt'}), call.update_state(state='PROGRESS', meta={'status': 66, 'file': u'file3.txt'})])
        mock_curl.perform.assert_has_calls(calls)

        # test modify files
        mock_curl.perform = MagicMock(name='curl_perform_modified', side_effect=['content modified file1', 'content modified file3'])
        payload = self.payload.bb_payload_modified()
        task = TaskFactory(service=self.service_bb)
        deploy = Deploy('host', payload, self.service_ftp_bb, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_bb.pk)
        self.assertTrue(service.log_set.all()[1].status)
        self.assertEqual(self.ftp_read_file(ftp, 'file1.txt'), 'content modified file1')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/folder2/folder3/file3.txt'), 'content modified file3')

        # test remove files 1
        payload = self.payload.bb_payload_removed1()
        task = TaskFactory(service=self.service_bb)
        deploy = Deploy('host', payload, self.service_ftp_bb, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_bb.pk)
        self.assertTrue(service.log_set.all()[2].status)
        self.assertNotIn('folder2', ftp.nlst('folder1'))

        # test remove files 2
        payload = self.payload.bb_payload_removed2()
        task = TaskFactory(service=self.service_bb)
        deploy = Deploy('host', payload, self.service_ftp_bb, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_bb.pk)
        self.assertTrue(service.log_set.all()[3].status)
        self.assertNotIn('folder1', ftp.nlst())
        self.assertNotIn('file1.txt', ftp.nlst())

        ftp.quit()

    @patch('ftp_deploy.utils.deploy.current_task')
    @patch('ftp_deploy.utils.deploy.curl_connection')
    def test_deploy_view_ftp_transfer_gh_data(self, mock_curl_connection, mock_current_task):
        """deploy view transfer data from bitbucket to ftp"""
        ftp = self.ftp_connection()
        mock_curl = MagicMock(name='curl')
        mock_curl_connection.return_value = mock_curl

        mock_curl.perform = MagicMock(name='curl_perform_added', side_effect=['content added file1', 'content added file2', 'content added file3'])
        # test create files
        payload = self.payload.gh_payload_added()
        task = TaskFactory(service=self.service_gh)
        deploy = Deploy('host', payload, self.service_ftp_gh, task.name)
        deploy.perform()

        service = Service.objects.get(pk=self.service_ftp_gh.pk)
        self.assertTrue(service.log_set.all()[0].status)

            # test task is removed after success deploy
        self.assertFalse(service.task_set.all().exists())

        self.assertEqual(self.ftp_read_file(ftp, 'file1.txt'), 'content added file1')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/file2.txt'), 'content added file2')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/folder2/folder3/file3.txt'), 'content added file3')
        mock_curl.assert_has_calls([call.authenticate(), call.close()])

        calls = ([call('https://raw.github.com/Owner/repo_slug/2fa93a45f6c4f9fe30e54036fe0cf764fae0b2a2/file1.txt'),
                  call('https://raw.github.com/Owner/repo_slug/2fa93a45f6c4f9fe30e54036fe0cf764fae0b2a2/folder1/file2.txt'),
                  call('https://raw.github.com/Owner/repo_slug/2fa93a45f6c4f9fe30e54036fe0cf764fae0b2a2/folder1/folder2/folder3/file3.txt')])

        # test celery update progress
        mock_current_task.assert_has_calls([call.update_state(state='PROGRESS', meta={'status': 0, 'file': u'file1.txt'}), call.update_state(
            state='PROGRESS', meta={'status': 33, 'file': u'file2.txt'}), call.update_state(state='PROGRESS', meta={'status': 66, 'file': u'file3.txt'})])
        mock_curl.perform.assert_has_calls(calls)

        # test modify files
        mock_curl.perform = MagicMock(name='curl_perform_modified', side_effect=['content modified file1', 'content modified file3'])
        payload = self.payload.gh_payload_modified()
        task = TaskFactory(service=self.service_gh)
        deploy = Deploy('host', payload, self.service_ftp_gh, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_gh.pk)
        self.assertTrue(service.log_set.all()[1].status)
        self.assertEqual(self.ftp_read_file(ftp, 'file1.txt'), 'content modified file1')
        self.assertEqual(self.ftp_read_file(ftp, 'folder1/folder2/folder3/file3.txt'), 'content modified file3')

        # test remove files 1
        payload = self.payload.gh_payload_removed1()
        task = TaskFactory(service=self.service_gh)
        deploy = Deploy('host', payload, self.service_ftp_gh, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_gh.pk)
        self.assertTrue(service.log_set.all()[2].status)
        self.assertNotIn('folder2', ftp.nlst('folder1'))

        # test remove files 2
        payload = self.payload.gh_payload_removed2()
        task = TaskFactory(service=self.service_gh)
        deploy = Deploy('host', payload, self.service_ftp_gh, task.name)
        deploy.perform()
        service = Service.objects.get(pk=self.service_ftp_gh.pk)
        self.assertTrue(service.log_set.all()[3].status)
        self.assertNotIn('folder1', ftp.nlst())
        self.assertNotIn('file1.txt', ftp.nlst())

        ftp.quit()    
