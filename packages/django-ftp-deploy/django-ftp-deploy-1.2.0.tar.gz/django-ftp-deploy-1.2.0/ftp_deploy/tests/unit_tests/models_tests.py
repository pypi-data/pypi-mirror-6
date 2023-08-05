from django.test import TestCase
from django.core.urlresolvers import reverse

from ftp_deploy.tests.utils.factories import ServiceFactory
from ftp_deploy.tests.utils.factories import NotificationFactory
from ftp_deploy.tests.utils.factories import LogFactory

from ftp_deploy.models import Log


class ServiceTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory.build()
        self.service.check = False
        self.service.save()

    def test_service_deploy_method(self):
        """service deploy method return number of related logs"""
        self.assertEqual(self.service.deploys(), 0)
        log = LogFactory(service=self.service)

        self.assertEqual(self.service.deploys(), 1)

        log.status = False
        log.save()

        self.assertEqual(self.service.deploys(), 0)

    def test_service_fail_deploys_method(self):
        """"service fail_deploy method return number of related logs with status False"""
        log = LogFactory(service=self.service)
        self.assertEqual(self.service.fail_deploys(), 0)
        log.status = False
        log.save()

        self.assertEqual(self.service.fail_deploys(), 1)

    def test_service_skipped_deploys_method(self):
        """service skipped_deploys method return number of relatet logs with skiped status True """
        log = LogFactory(service=self.service)

        self.assertEqual(self.service.skipped_deploys(), 0)

        log.status = False
        log.skip = True
        log.save()

        self.assertEqual(self.service.skipped_deploys(), 1)

    def test_service_latest_log_date_method(self):
        """service latest_log_date method return latest related log create date"""
        log1 = LogFactory(service=self.service)
        log2 = LogFactory(service=self.service)
        self.assertEqual(self.service.latest_log_date(), self.service.log_set.latest('created').created)

    def test_service_latest_log_user_method(self):
        """service latest_log_user method return latest related log user"""
        log1 = LogFactory(service=self.service)
        log2 = LogFactory(service=self.service)
        self.assertEqual(self.service.latest_log_user(), self.service.log_set.latest('created').user)

    def test_service_hook_url_method(self):
        """service hook_url method return hook url for appropriate repository"""
        self.assertEqual(self.service.hook_url(), reverse('ftpdeploy_deploy', kwargs={'secret_key': self.service.secret_key}))


class LogTest(TestCase):

    def setUp(self):
        self.service = ServiceFactory.build()
        self.service.check = False
        self.service.save()

    def test_commits_info_method(self):
        """log commits_info method return commits information in format [[message,username,raw_node],]"""
        log = LogFactory(service=self.service)

        self.assertEqual(log.commits_info(), [[u'test message commit 2', u'username', u'57baa5c89daef238c2043c7e866c2e997d681876'], [
                                              u'test message commit 1', u'username', u'57baa5c89daef238c2043c7e866c2e997d681871']])


class NotificationTest(TestCase):

    def setUp(self):
        self.notification = NotificationFactory()

    def test_notification_get_email_list_method(self):
        """
        notification get_email_list methos return email list in format 
        {{'email1@email.com': {'success': True}, 'email2@email.com': {'success': True}, 
            'email1@email.com': {'fail': True}, 'email2@email.com': {'fail': True}}}
        """
        success = self.notification.get_success()
        fail = self.notification.get_fail()

        email_list = {success[0]: {'success': True}, success[1]: {
                      'success': True}, fail[0]: {'fail': True}, fail[1]: {'fail': True}}

        self.assertEqual(self.notification.get_email_list(), email_list)

    def test_notification_user_methods(self):
        """notification user_commits_success and user_deploy_fail... methods return True of False according to settings"""
        self.assertEqual(self.notification.commit_user_success(), True)
        self.assertEqual(self.notification.commit_user_fail(), True)
        self.assertEqual(self.notification.deploy_user_success(), True)
        self.assertEqual(self.notification.deploy_user_fail(), True)

        self.notification.commit_user = [u'1']
        self.notification.deploy_user = []
        self.notification.save()

        self.assertEqual(self.notification.commit_user_success(), False)
        self.assertEqual(self.notification.commit_user_fail(), True)
        self.assertEqual(self.notification.deploy_user_success(), False)
        self.assertEqual(self.notification.deploy_user_fail(), False)
