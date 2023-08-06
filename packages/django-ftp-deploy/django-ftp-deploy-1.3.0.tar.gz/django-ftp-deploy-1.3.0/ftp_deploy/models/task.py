import json
from django.db import models

from ftp_deploy.utils.core import commits_parser
from .service import Service

class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    service = models.ForeignKey(Service)
    active = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'ftp_deploy'
        db_table = 'ftp_deploy_task'
