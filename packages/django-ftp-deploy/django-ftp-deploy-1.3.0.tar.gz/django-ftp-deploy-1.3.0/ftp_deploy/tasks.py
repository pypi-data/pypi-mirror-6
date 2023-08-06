from __future__ import absolute_import

from celery import task, current_task

from .celery import app
from .utils.deploy import Deploy
from .models import Task

@app.task
def deploy_task(host,payload,service):
    deploy = Deploy(host, payload, service, deploy_task.request.id)
    deploy.perform()

    


