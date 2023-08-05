# -*- coding: utf-8 -*-
import os
import json
from ftplib import FTP
import tempfile

from django.views.generic.base import View
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Log, Service
from .conf import *
from .utils.core import absolute_url, LockError
from .utils.ftp import ftp_connection
from .utils.email import notification_success, notification_fail
from .utils.curl import curl_connection


class DeployView(View):

    """Main view receive POST Hook from repository"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        try:
            self.service = Service.objects.get(secret_key=kwargs['secret_key'])
        except Exception, e:
            raise Http404

        self.status = 200

        self.bitbucket_username = BITBUCKET_SETTINGS['username']
        self.bitbucket_password = BITBUCKET_SETTINGS['password']
        self.bitbucket_branch = self.service.repo_branch

        self.ftp_host = self.service.ftp_host
        self.ftp_username = self.service.ftp_username
        self.ftp_password = self.service.ftp_password
        self.ftp_path = self.service.ftp_path

        return super(DeployView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.json_string = request.POST['payload'].decode('string_escape').replace('\n', '')
        self.data = json.loads(self.json_string)
        last_commit = len(self.data['commits']) - 1


        if self.data['commits'][last_commit]['branch'] == self.bitbucket_branch:
            self.log = Log()
            self.log.payload = self.json_string
            self.log.service = self.service
            self.log.save()

            try:
                self.ftp = ftp_connection(self.ftp_host, self.ftp_username, self.ftp_password, self.ftp_path)

                if self.service.lock:
                    raise LockError()

                self.service.check = False
                self.service.lock = True
                self.service.save()

                self.ftp.connect()

            except LockError, e:
                self.set_fail(request, 'Service Locked', e)
            except Exception, e:
                self.set_fail(request, 'FTP Connection', e)
            else:
                try:
                    curl = curl_connection(self.bitbucket_username, self.bitbucket_password)
                    curl.authenticate()

                    for i, commit in enumerate(self.data['commits']):

                        for files in commit['files']:
                            file_path = files['file']

                            if files['type'] == 'removed':
                                self.ftp.remove_file(file_path)
                            else:
                                url = 'https://api.bitbucket.org/1.0/repositories%sraw/%s/%s' % (self.data['repository']['absolute_url'], commit['node'], file_path)
                                url = str(url.encode('utf-8'))

                                value = curl.perform(url)

                                temp_file = tempfile.NamedTemporaryFile(delete=False)
                                temp_file.write(value)
                                temp_file.close()
                                temp_file = open(temp_file.name, 'rb')

                                self.ftp.make_dirs(file_path)
                                self.ftp.create_file(file_path, temp_file)

                                temp_file.close()
                                os.unlink(temp_file.name)

                except Exception, e:
                    self.set_fail(request, self.data['user'], e)
                else:
                    self.log.user = self.data['user']
                    self.log.status = True
                    self.log.save()
                    notification_success(absolute_url(request).build(), self.service, self.json_string)
                finally:
                    curl.close()

            finally:
                self.ftp.quit()
                self.service.lock = False
                self.service.check = True
                self.service.save()

        return HttpResponse(status=self.status)

    def set_fail(self, request, user, message):
        self.log.user = user
        self.log.status_message = message
        self.log.status = False
        self.log.save()
        self.service.status = False
        self.status = 500
        notification_fail(absolute_url(request).build(), self.service, self.json_string, message)
