import os
import json
from ftplib import FTP
import tempfile
import time
from celery import task, current_task

from ftp_deploy.conf import *
from ftp_deploy.models import Log, Task
from .core import LockError, commits_parser
from .ftp import ftp_connection
from .email import notification_success, notification_fail
from .curl import curl_connection


class Deploy(object):

    """Deploy method responsible for perform deploying"""

    def __init__(self, host, payload, service, task_name):
        self.host = host
        self.service = service
        self.task = Task.objects.get(name=task_name)
        self.data = json.loads(payload)
        self.json_string = payload
        self.files_count = commits_parser(self.data['commits']).files_count()

        self.ftp_host = self.service.ftp_host
        self.ftp_username = self.service.ftp_username
        self.ftp_password = self.service.ftp_password
        self.ftp_path = self.service.ftp_path

        self.bitbucket_username = BITBUCKET_SETTINGS['username']
        self.bitbucket_password = BITBUCKET_SETTINGS['password']

    def perform(self):
        """Perform ftp connection and choose repository perform method (bitbucket or github)"""

        if self.data['user'] == 'Restore':
            self.service.get_logs_tree().delete()

        self.log = Log()
        self.log.payload = self.json_string
        self.log.service = self.service
        self.log.save()

        try:
            self.ftp = ftp_connection(self.ftp_host, self.ftp_username, self.ftp_password, self.ftp_path)

            if self.service.lock():
                raise LockError()

            self.task.active = True
            self.task.save()

            self.ftp.connect()

        except LockError, e:
            self.set_fail('Service Locked', e)
        except Exception, e:
            self.set_fail('FTP Connection', e)
        else:
            try:

                if self.service.repo_source == 'bb':
                    self.perform_bitbucket()

                if self.service.repo_source == 'gh':
                    self.perform_github()

            except Exception, e:
                self.set_fail(self.data['user'], e)
            else:
                self.log.user = self.data['user']
                self.log.status = True
                self.log.save()
                notification_success(self.host, self.service, self.json_string)

        finally:
            self.ftp.quit()
            self.service.check()
            self.service.save()
            self.task.delete()

    def perform_bitbucket(self):
        """perform bitbucket deploy"""
        curl = curl_connection(self.bitbucket_username, self.bitbucket_password)
        curl.authenticate()
        i = 0
        for commit in self.data['commits']:
            for files in commit['files']:
                file_path = files['file']
                
                self.update_progress(i,file_path)
                i += 1

                if files['type'] == 'removed':
                    self.ftp.remove_file(file_path)
                else:
                    url = 'https://api.bitbucket.org/1.0/repositories%sraw/%s/%s' % (self.data['repository']['absolute_url'], commit['node'], file_path)
                    url = str(url.encode('utf-8'))

                    value = curl.perform(url)
                    self.create_file(file_path,value)

        curl.close()

    def perform_github(self):
        pass

    def update_progress(self,i,file_path):
        progress_percent = int(100 * float(i) / float(self.files_count))
        current_task.update_state(state='PROGRESS', meta={'status': progress_percent, 'file': os.path.basename(file_path)})

    def create_file(self,file_path,value):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(value)
        temp_file.close()
        temp_file = open(temp_file.name, 'rb')

        self.ftp.make_dirs(file_path)
        self.ftp.create_file(file_path, temp_file)

        temp_file.close()
        os.unlink(temp_file.name)

    def set_fail(self, user, message):
        self.log.user = user
        self.log.status_message = message
        self.log.status = False
        self.log.save()
        notification_fail(self.host, self.service, self.json_string, message)
