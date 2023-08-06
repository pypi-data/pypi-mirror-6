import json
import certifi
import pycurl

from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory

from mock import MagicMock
from mock import PropertyMock
from mock import patch
from mock import call

from ftp_deploy.conf import *
from ftp_deploy.models import Log
from ftp_deploy.utils.decorators import check
from ftp_deploy.utils.core import commits_parser, absolute_url, LockError, service_check, bitbucket_check
from ftp_deploy.utils.email import notification_success, notification_fail
from ftp_deploy.utils.ftp import ftp_check, ftp_connection
from ftp_deploy.utils.curl import curl_connection

from ftp_deploy.tests.utils.factories import ServiceFactory,LogFactory, NotificationFactory
from ftp_deploy.models.service import Service


class UtilsDecoratorCheckTest(TestCase):

    def test_utils_decorator_check_exception_output(self):
        """check decorator return tuple in format (True, '<b>prefix:</b> Exception message') if raise exception"""
        check_ = check('prefix')
        output = check_(self.function_raise_exception)()
        self.assertEqual(output, (True, '<b>prefix:</b> Exception message'))

    def test_utils_decorator_check_no_exception_output(self):
        """check decorator return tuple in format (False,'') if no exception"""
        check_ = check('prefix')
        output = check_(self.function_not_raise_exception)()
        self.assertEqual(output, (False, ''))

    def function_raise_exception(self):
        raise Exception("Exception message")

    def function_not_raise_exception(self):
        pass


class UtilsCoreServiceCheckTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()

    def test_service_check_init(self):
        """service test init set up service, message and fails list"""

        check_init = service_check(self.service)

        self.assertEqual(check_init.service, self.service)
        self.assertEqual(check_init.message, [])
        self.assertEqual(check_init.fails, [False, False, False, False])

    def test_service_check_log_return_number_of_fail_logs_assign_to_service(self):
        log1 = LogFactory(service=self.service, status=False)
        log2 = LogFactory(service=self.service, status=False)
        log3 = LogFactory(service=self.service, status=True)

        check_log = service_check(self.service)
        check_log.check_log()

        self.assertEqual(check_log.message, ['<b>Log</b>: Deploy Fails(2)'])
        self.assertTrue(check_log.fails[0])

    @patch('ftp_deploy.utils.core.bitbucket_check')
    def test_service_check_repo_bb_perform_bb_check_and_return_proper_data(self, mock_bb_check):
        bb = MagicMock(name='bb', spec_set=bitbucket_check)
        mock_bb_check.return_value = bb
        bb.check_all = MagicMock(name='check_all', return_value=(True, 'bb_fail'))
        bb.check_hook_exist = MagicMock(name='check_hook_exist', return_value=(True, 'bb_hook_fail'))

        check_repo = service_check(self.service)
        check_repo.check_repo()

        mock_bb_check.assert_called_once_with(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'], self.service)
        self.assertEqual(check_repo.message, ['bb_fail', 'bb_hook_fail'])
        self.assertTrue(check_repo.fails[1])
        self.assertTrue(check_repo.fails[2])

    @patch('ftp_deploy.utils.core.ftp_check')
    def test_service_check_ftp_perform_ftp_check_and_return_proper_data(self, mock_ftp_check):
        ftp = MagicMock(name='ftp', spec_set=ftp_check)
        mock_ftp_check.return_value = ftp
        ftp.check_all = MagicMock(name='check_all', return_value=(True, 'ftp_fail'))

        check_ftp = service_check(self.service)
        check_ftp.check_ftp()

        mock_ftp_check.assert_called_once_with('ftp_host', 'ftp_username', 'ftp_password', 'ftp/path')
        self.assertEqual(check_ftp.message, ['ftp_fail'])
        self.assertTrue(check_ftp.fails[3])

    @patch('ftp_deploy.utils.core.service_check.check_log')
    @patch('ftp_deploy.utils.core.service_check.check_repo')
    @patch('ftp_deploy.utils.core.service_check.check_ftp')
    def test_service_check_all_perform_all_check_stages_and_return_proper_data(self, mock_check_log, mock_check_repo, mock_check_ftp):
        check_all = service_check(self.service)
        check_all.fails = 'fails'
        check_all.message = 'message'
        response = check_all.check_all()

        mock_check_log.assert_called_with()
        mock_check_repo.assert_called_with()
        mock_check_ftp.assert_called_with()
        self.assertEqual(response, ('fails', 'message'))


class UtilsCoreCommitParserTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory()

        log = LogFactory(service=self.service)
        payload = json.loads(log.payload)
        self.data = commits_parser(payload['commits'])

    def test_commit_parser_file_diff(self):
        """file_diff return files information in format - files_added, files_modified, files_removed"""
        files_added, files_modified, files_removed = self.data.file_diff()

        self.assertEqual(files_added[0], 'example/file2.txt')
        self.assertEqual(files_modified[0], 'example/file1.txt')
        self.assertEqual(files_removed[0], 'example/file3.txt')
        self.assertNotIn('example/file4.txt', files_removed)

    def test_commit_parser_commits_info(self):
        """commits_info return commits info in format [['message','username','raw_node'],]"""
        commits_info = self.data.commits_info()
        self.assertEqual(commits_info, [[u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [
                         u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871']])

    def test_commit_parser_email_list_return_list_of_emails_from_commits(self):
        email_list = self.data.email_list()
        self.assertEqual(email_list, [u'author@email.com'])


class UtilsCoreAbsoluteURLTest(TestCase):

    def test_absoluteurl_build_return_absolute_url_of_the_website(self):
        request_factory = RequestFactory()
        request = request_factory.get('/example')
        output = absolute_url(request).build()
        self.assertEqual(output, 'http://testserver')


class UtilsCoreLockErrorTest(TestCase):

    def test_lock_error_exception(self):
        try:
            raise LockError()
        except LockError, e:
            self.assertEqual(e.__str__(), 'Deploy failed because service is Locked!')


class UtilsEmailTest(TestCase):

    def setUp(self):
        notification = NotificationFactory(
            success='email_success_1@email.com,email_success_1@email.com,email_success_2@email.com',
            fail='email_fail_1@email.com,email_fail_2@email.com',
            deploy_user=[]
        )

        self.service = ServiceFactory(notification=notification)
        self.log = LogFactory(service=self.service)

        request_factory = RequestFactory()
        request = request_factory.get('/example')
        self.host = absolute_url(request).build()

    def test_notification_success_subject(self):
        notification = notification_success(self.host, self.service, self.log.payload)
        self.assertEqual(notification.subject(), '%s - Deploy Successfully' % self.service)

    def test_notification_success_emails_list(self):
        notification = notification_success(self.host, self.service, self.log.payload)
        self.assertIn('email_success_1@email.com', notification.emails())
        self.assertIn('email_success_2@email.com', notification.emails())
        self.assertIn('author@email.com', notification.emails())

    def test_notification_success_emails_no_notification(self):
        """recipient email list for success email is empty if service has no notification assign"""
        self.service.notification = None
        notification = notification_success(self.host, self.service, self.log.payload)
        self.assertListEqual(notification.emails(), [])

    def test_notification_success_context(self):
        notification = notification_success(self.host, self.service, self.log.payload)

        payload = json.loads(self.log.payload)
        files_added, files_modified, files_removed = commits_parser(payload['commits']).file_diff()

        self.assertEqual(notification.context()['service'], self.service)
        self.assertEqual(notification.context()['host'], self.host)
        self.assertEqual(notification.context()['commits_info'], commits_parser(payload['commits']).commits_info())
        self.assertEqual(notification.context()['files_added'], files_added)
        self.assertEqual(notification.context()['files_modified'], files_modified)
        self.assertEqual(notification.context()['files_removed'], files_removed)

    def test_notification_fail_subject(self):
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')
        self.assertEqual(notification.subject(), '%s - Deploy Fail' % self.service)

    def test_notification_fail_emails_list(self):
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')
        self.assertIn('email_fail_1@email.com', notification.emails())
        self.assertIn('email_fail_2@email.com', notification.emails())

    def test_notification_fail_emails_no_notification(self):
        """recipient email list for fail email is empty if service has no notification assign"""
        self.service.notification = None
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')
        self.assertListEqual(notification.emails(), [])

    def test_notification_fail_context(self):
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')

        self.assertEqual(notification.context()['service'], self.service)
        self.assertEqual(notification.context()['host'], self.host)
        self.assertEqual(notification.context()['error'], 'error_message')

    def test_notification_send_method_sent_appropriate_number_of_emails(self):
        notification_success(self.host, self.service, self.log.payload)
        self.assertEqual(len(mail.outbox), 3)


class UtilsCurlTest(TestCase):

    def test_curl_connection_init_setup_username_and_password(self):
        """curl connection set up username and password"""
        curl = curl_connection('curl_username', 'curl_password')
        self.assertEqual(curl.username, 'curl_username')
        self.assertEqual(curl.password, 'curl_password')

    @patch('ftp_deploy.utils.curl.certifi')
    @patch('ftp_deploy.utils.curl.pycurl')
    def test_curl_authenticate_method_perform_curl_authorisation(self, mock_pycurl, mock_certifi):
        mock_certifi.where.return_value = 'certifi_where'
        mock_curl = MagicMock(name='curl')
        mock_pycurl.Curl.return_value = mock_curl
        type(mock_curl).USERPWD = PropertyMock(name='MOCK_USERPWD', return_value='USERPWD')
        type(mock_pycurl).CAINFO = PropertyMock(name='MOCK_CAINFO', return_value='CAINFO')

        curl = curl_connection('curl_username', 'curl_password')
        curl.authenticate()

        mock_pycurl.assert_has_calls([call.Curl()])
        mock_curl.assert_has_calls([call.setopt('CAINFO', 'certifi_where'), call.setopt('USERPWD', 'curl_username:curl_password')])

    @patch('ftp_deploy.utils.curl.StringIO')
    def test_curl_perform_method_perform_curl_GET_request(self, mock_stringIO):
        type(mock_stringIO.StringIO()).write = PropertyMock(name='io_write', return_value='io_write')

        curl = curl_connection('curl_username', 'curl_password')
        curl.curl = MagicMock(name='mock_curl')
        type(curl.curl).URL = PropertyMock(name='MOCK_URL', return_value='URL')
        type(curl.curl).WRITEFUNCTION = PropertyMock(name='MOCK_WRITEFUNCTION', return_value='WRITEFUNCTION')
        curl.perform('example/url')

        curl.curl.assert_has_calls([call.setopt('URL', 'example/url'), call.setopt('WRITEFUNCTION', 'io_write'), call.perform()])

    def test_curl_perform_post_method_senf_POST_request_with_post_data(self):
        curl = curl_connection('curl_username', 'curl_password')
        curl.curl = MagicMock(name='mock_curl')
        type(curl.curl).URL = PropertyMock(name='MOCK_URL', return_value='URL')
        type(curl.curl).POSTFIELDS = PropertyMock(name='MOCK_POSTFIELDS', return_value='POSTFIELDS')

        curl.perform_post('example/url', 'post=data')

        curl.curl.assert_has_calls([call.setopt('URL', 'example/url'), call.setopt('POSTFIELDS', 'post=data'), call.perform()])

    @patch('ftp_deploy.utils.curl.pycurl')
    def test_curl_get_http_code_method_return_http_response_of_current_curl_request(self, mock_pycurl):
        type(mock_pycurl).HTTP_CODE = PropertyMock(return_value='HTTP_CODE')
        curl = curl_connection('curl_username', 'curl_password')
        curl.curl = MagicMock(name='mock_curl')
        curl.get_http_code()
        curl.curl.assert_has_calls(call.getinfo('HTTP_CODE'))

    def test_curl_close_method_close_current_curl_connection(self):
        curl = curl_connection('curl_username', 'curl_password')
        curl.curl = MagicMock(name='mock_curl')
        curl.close()
        curl.curl.assert_has_calls(call.close())


class UtilsFTPTest(TestCase):

    def setUp(self):
        self.ftp_connection = ftp_connection('host', 'username', 'password', 'ftp/path/')

    def test_ftp_connection_init_method_setup_variables(self):
        self.assertEqual(self.ftp_connection.host, 'host')
        self.assertEqual(self.ftp_connection.username, 'username')
        self.assertEqual(self.ftp_connection.password, 'password')
        self.assertEqual(self.ftp_connection.ftp_path, 'ftp/path/')
        self.assertFalse(self.ftp_connection.connected)

    @patch('ftp_deploy.utils.ftp.FTP')
    def test_ftp_connection_connect_method_perform_login_to_ftp(self, mock_ftp):
        self.ftp_connection.connect()
        mock_ftp.assert_has_calls([call('host'), call().login('username', 'password')])
        self.assertTrue(self.ftp_connection.connected)

    def test_ftp_connection_create_file_method_create_file_in_filepath_location(self):
        self.ftp_connection.ftp = MagicMock(name='ftp')
        self.ftp_connection.create_file('path/to/file/file.txt', 'example file content')
        self.ftp_connection.ftp.assert_has_calls(call.storbinary('STOR ftp/path/path/to/file/file.txt', 'example file content'))

    def test_ftp_connection_remove_file_method_remove_file_and_clear_empty_directories(self):
        return_default = lambda value: value
        self.ftp_connection.ftp = MagicMock(name='ftp')
        self.ftp_connection.ftp.rmd = MagicMock(name='rmd',side_effect=[return_default, Exception('no empty directory')])
        self.ftp_connection.remove_file('path/to/file/file.txt')

        self.ftp_connection.ftp.rmd.assert_has_calls([call('ftp/path/path/to/file'), call('ftp/path/path/to')])
        self.ftp_connection.ftp.assert_has_calls([call.delete('ftp/path/path/to/file/file.txt')])

    def test_ftp_connection_make_dirs_method_create_all_directories_based_on_filepath(self):
        return_default = lambda value: value
        self.ftp_connection.ftp = MagicMock(name='ftp')
        self.ftp_connection.ftp.dir = MagicMock(name='dir', side_effect=[return_default, Exception('directory doesnt exist')])
        self.ftp_connection.ftp.mkd = MagicMock(name='mkd')
        self.ftp_connection.make_dirs('path/to/file/file.txt')

        self.ftp_connection.ftp.dir.assert_has_calls([call('ftp/path/path'), call('ftp/path/path/to'), call('ftp/path/path/to/file')])
        self.ftp_connection.ftp.mkd.assert_has_calls([call('ftp/path/path/to'), call('ftp/path/path/to/file')])

    def test_ftp_connection_quit_mehtod_perform_quit_only_if_connected_is_true(self):
        self.ftp_connection.ftp = MagicMock(name='ftp')
        self.ftp_connection.connected = True
        self.ftp_connection.quit()
        self.ftp_connection.ftp.assert_has_calls([call.quit()])

        self.ftp_connection.connected = False
        self.ftp_connection.quit()
        self.assertFalse(self.ftp_connection.ftp.called)

    def test_ftp_check_login_perfrm_connect_method(self):
        check = ftp_check('host', 'username', 'password', 'ftp/path/')
        check.connect = MagicMock(name='connect')
        check.check_ftp_login()
        self.assertTrue(check.connect.mock_called)

    def test_ftp_check_if_path_exist(self):
        check = ftp_check('host', 'username', 'password', 'ftp/path/')
        check.ftp = MagicMock(name='ftp')
        check.check_ftp_path()

        check.ftp.assert_has_calls([call.cwd('ftp/path/')])

    def test_ftp_check_all_perform_all_check_stages(self):
        check = ftp_check('host', 'username', 'password', 'ftp/path/')
        check.check_ftp_login = MagicMock(name='check_login', return_value=(True, 'error login message'))
        check.check_ftp_path = MagicMock(name='check_ftp_path', return_value=(True, 'error path message'))
        response = check.check_all()
        self.assertEqual(response, (True, 'error login message'))

        check.check_ftp_login = MagicMock(name='check_login', return_value=(False, ''))
        check.check_ftp_path = MagicMock(name='check_ftp_path', return_value=(True, 'error path message'))
        response = check.check_all()
        self.assertEqual(response, (True, 'error path message'))

        check.check_ftp_login = MagicMock(name='check_login', return_value=(False, ''))
        check.check_ftp_path = MagicMock(name='check_ftp_path', return_value=(False, ''))
        response = check.check_all()
        self.assertEqual(response, (False, ''))
