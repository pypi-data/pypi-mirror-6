import json

from django.test import TestCase
from django.test.client import RequestFactory

from ftp_deploy.models import Log
from ftp_deploy.utils.decorators import check
from ftp_deploy.utils.core import commits_parser
from ftp_deploy.utils.core import absolute_url
from ftp_deploy.utils.core import LockError
from ftp_deploy.utils.email import notification_success
from ftp_deploy.utils.email import notification_fail

from ftp_deploy.tests.utils.factories import ServiceFactory
from ftp_deploy.tests.utils.factories import LogFactory
from ftp_deploy.tests.utils.factories import NotificationFactory


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


class UtilsCoreCommitParserTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory.build()
        self.service.check = False
        self.service.save()

        log = LogFactory(service=self.service)
        payload = json.loads(log.payload)
        self.data = commits_parser(payload['commits'])

    def test_commit_parser_file_diff(self):
        """file_diff return files information in format - files_added, files_modified, files_removed"""
        files_added, files_modified, files_removed = self.data.file_diff()
        self.assertEqual(files_added[0], 'example/file2.txt')
        self.assertEqual(files_modified[0], 'example/file1.txt')
        self.assertEqual(files_removed[0], 'example/file3.txt')

    def test_commit_parser_commits_info(self):
        """commits_info return commits info in format [['message','username','raw_node'],]"""
        commits_info = self.data.commits_info()
        self.assertEqual(commits_info, [[u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [
                         u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871']])

    def test_commit_parser_email_list(self):
        """email_list return list of emails from commits"""
        email_list = self.data.email_list()
        self.assertEqual(email_list, [u'author@email.com'])


class UtilsCoreAbsoluteURLTest(TestCase):

    def test_absoluteurl_build(self):
        """absolute_url return absolute url of the website"""
        request_factory = RequestFactory()
        request = request_factory.get('/example')
        output = absolute_url(request).build()
        self.assertEqual(output, 'http://testserver')


class UtilsCoreLockErrorTest(TestCase):

    def test_lock_error_exception(self):
        """lock error exception return string 'Deploy failed because service is Locked!'"""
        try:
            raise LockError()
        except LockError, e:
            self.assertEqual(e.__str__(), 'Deploy failed because service is Locked!')


class UtilsEmailTest(TestCase):

    def setUp(self):
        notification = NotificationFactory(
            success='email_success_1@email.com,email_success_2@email.com',
            fail='email_fail_1@email.com,email_fail_2@email.com',
            deploy_user=[]
        )

        self.service = ServiceFactory.build(notification=notification)
        self.service.check = False
        self.service.save()

        self.log = LogFactory(service=self.service)

        request_factory = RequestFactory()
        request = request_factory.get('/example')
        self.host = absolute_url(request).build()

    def test_notification_success_subject(self):
        """Test subject for success notification email"""
        notification = notification_success(self.host, self.service, self.log.payload)
        self.assertEqual(notification.subject(), '%s - Deploy Successfully' % self.service)

    def test_notification_success_emails_notification(self):
        """Test recipient email list for success email notification"""
        notification = notification_success(self.host, self.service, self.log.payload)
        self.assertIn('email_success_1@email.com', notification.emails())
        self.assertIn('email_success_2@email.com', notification.emails())

    def test_notification_success_emails_no_notification(self):
        """recipient email list for success email is empty if service has no notification assign"""
        self.service.notification = None
        notification = notification_success(self.host, self.service, self.log.payload)
        self.assertListEqual(notification.emails(), [])

    def test_notification_success_context(self):
        """test context information for success notification template"""
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
        """Test subject for fail notification email"""
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')
        self.assertEqual(notification.subject(), '%s - Deploy Fail' % self.service)

    def test_notification_fail_emails_notification(self):
        """Test recipient email list for fail email notification"""
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')
        self.assertIn('email_fail_1@email.com', notification.emails())
        self.assertIn('email_fail_2@email.com', notification.emails())

    def test_notification_fail_emails_no_notification(self):
        """recipient email list for fail email is empty if service has no notification assign"""
        self.service.notification = None
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')
        self.assertListEqual(notification.emails(), [])

    def test_notification_fail_context(self):
        """test context information for fail notification template"""
        notification = notification_fail(self.host, self.service, self.log.payload, 'error_message')

        self.assertEqual(notification.context()['service'], self.service)
        self.assertEqual(notification.context()['host'], self.host)
        self.assertEqual(notification.context()['error'], 'error_message')
