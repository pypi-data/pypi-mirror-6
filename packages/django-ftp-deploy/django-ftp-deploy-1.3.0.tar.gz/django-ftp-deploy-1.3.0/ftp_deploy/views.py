from __future__ import absolute_import
import os
import json
from ftplib import FTP
import tempfile
from celery.result import AsyncResult

from django.views.generic.base import View
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Service, Log, Task
from .utils.core import absolute_url
from .tasks import deploy_task
from .utils.deploy import Deploy

import time


class DeployView(View):

    """Main view receive POST Hook from repository"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        try:
            self.service = Service.objects.get(secret_key=kwargs['secret_key'])
        except Exception, e:
            raise Http404

        self.service_pk = str(self.service.pk)
        return super(DeployView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        json_string = request.POST['payload'].decode('string_escape').replace('\n', '')
        data = json.loads(json_string)

        if(self.check_branch(data)):
            host = absolute_url(request).build()
            job = deploy_task.apply_async((host, json_string, self.service), countdown=1)
            Task.objects.create(name=job.id, service=self.service)

        return HttpResponse(status=200)

    def check_branch(self, data):
        """check if payload branch match set branch"""
        if self.service.repo_source == 'bb':
            last_commit = len(data['commits']) - 1
            if data['commits'][last_commit]['branch'] == self.service.repo_branch:
                return True

        if self.service.repo_source == 'gh':
            pass

        return False


class DeployStatusView(DeployView):

    def post(self, request, *args, **kwargs):
        data = dict()
        if self.service.has_queue():
            task_id = self.service.task_set.all()[0]
            task = AsyncResult(task_id.name)
            data = task.result or dict(status=task.state)

        data['queue'] = self.service.task_set.all().count()
        json_data = json.dumps(data)
        return HttpResponse(json_data, mimetype='application/json')

