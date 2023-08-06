import re
import pycurl
import certifi
import StringIO

from .ftp import ftp_check
from .repo import bitbucket_check, github_check
from ftp_deploy.conf import *


class service_check(object):

    """Service check class, what group together all checking points. Return 'fails' and 'message' lists"""

    def __init__(self, service):
        self.service = service
        self.message = list()
        self.fails = [False, False, False, False]

    def check_log(self):
        """Check logs"""
        if self.service.pk is not None:
            log_fail = self.service.log_set.all().filter(status=False).filter(skip=False).count()
            if log_fail:
                self.message.append('<b>Log</b>: Deploy Fails(%d)' % log_fail)
                self.fails[0] = True

    def check_repo(self):
        """Check repositories connection, along with POST Hook"""
        if self.service.repo_source == 'bb':
            repo = bitbucket_check(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'], self.service)
        elif self.service.repo_source == 'gh':
            repo = github_check(GITHUB_SETTINGS['username'], GITHUB_SETTINGS['password'], self.service)  

        repo_fail, repo_fail_message = repo.check_all()
        if repo_fail:
            self.message.append(repo_fail_message)
            self.fails[1] = True

        hook_fail, hook_fail_message = repo.check_hook_exist()
        if hook_fail:
            self.message.append(hook_fail_message)
            self.fails[2] = True

    def check_ftp(self):
        """Check FTP connection"""
        ftp = ftp_check(self.service.ftp_host, self.service.ftp_username, self.service.ftp_password, self.service.ftp_path)
        ftp_fail, ftp_fail_message = ftp.check_all()
        ftp.quit()

        if ftp_fail:
            self.message.append(ftp_fail_message)
            self.fails[3] = True

    def check_all(self):
        self.check_log()
        self.check_repo()
        self.check_ftp()

        return self.fails, self.message

class absolute_url(object):

    """Build absolute url to root url without trailing slash"""

    def __init__(self, request):
        self.request = request

    def build(self):
        return self.request.build_absolute_uri('/')[:-1]


class LockError(Exception):

    """Exception if service is locked"""

    def __str__(self):
        return 'Deploy failed because service is Locked!'


