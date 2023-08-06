import os
import factory
import random
import string
import logging

from django.contrib.auth.models import User
from ftp_deploy.models import Service, Notification, Log, Task

logger = logging.getLogger('factory')
logger.setLevel(logging.ERROR)


class NotificationFactory(factory.DjangoModelFactory):

    """Factory for Notification object"""
    FACTORY_FOR = Notification

    name = factory.Sequence(lambda n: 'notification_%d' % n)
    success = factory.Sequence(lambda n: 'email_success_%d@emai.com,email_success_%d@emai.com,' % (n, n + 1))
    fail = factory.Sequence(lambda n: 'email_fail_%d@emai.com,email_fail_%d@emai.com,' % (n, n + 1))
    commit_user = [u'0', u'1']
    deploy_user = [u'0', u'1']


class ServiceFactory(factory.DjangoModelFactory):

    """Factory for Service object"""
    FACTORY_FOR = Service

    ftp_host = 'ftp_host'
    ftp_username = 'ftp_username'
    ftp_password = 'ftp_password'
    ftp_path = 'ftp/path'

    repo_source = 'bb'
    repo_name = factory.Sequence(lambda n: 'repo_name_%d' % n)
    repo_slug_name = repo_name
    repo_branch = 'master'
    repo_hook = True

    status = True
    status_message = ''
    notification = factory.SubFactory(NotificationFactory)

    @factory.sequence
    def secret_key(n):
        return ''.join(random.choice(string.letters + string.digits) for x in range(30))


class LogFactory(factory.DjangoModelFactory):

    """Factory for Log object"""
    FACTORY_FOR = Log

    service = factory.SubFactory(ServiceFactory)
    user = factory.Sequence(lambda n: 'user_%d' % n)
    status = True
    status_message = ''

    @factory.LazyAttribute
    def payload(obj):
        if obj.service.repo_source == 'bb':
            with open('%s/payloads/bb_payload.txt' % os.path.dirname(__file__), 'r') as content_file:
                payload = content_file.read()
        elif obj.service.repo_source == 'gh':
            with open('%s/payloads/gh_payload.txt' % os.path.dirname(__file__), 'r') as content_file:
                payload = content_file.read()
        return payload

class TaskFactory(factory.DjangoModelFactory):

    """Factory for task object"""
    FACTORY_FOR = Task

    name = factory.Sequence(lambda n: 'factory_name_%d' % n)
    service = factory.SubFactory(ServiceFactory)
    active = False


class AdminUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    email = 'admin@admin.com'
    username = 'admin'
    password = factory.PostGenerationMethodCall('set_password', 'admin')

    is_superuser = True
    is_staff = True
    is_active = True
