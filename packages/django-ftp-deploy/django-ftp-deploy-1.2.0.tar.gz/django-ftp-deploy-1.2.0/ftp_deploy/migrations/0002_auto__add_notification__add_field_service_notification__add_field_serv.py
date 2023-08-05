# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Notification'
        db.create_table('ftp_deploy_notification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('success', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('fail', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('commit_user', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('deploy_user', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ftp_deploy', ['Notification'])

        # Adding field 'Service.notification'
        db.add_column('ftp_deploy_service', 'notification',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ftp_deploy.Notification'], null=True, on_delete=models.SET_NULL, blank=True),
                      keep_default=False)

        # Adding field 'Service.lock'
        db.add_column('ftp_deploy_service', 'lock',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Notification'
        db.delete_table('ftp_deploy_notification')

        # Deleting field 'Service.notification'
        db.delete_column('ftp_deploy_service', 'notification_id')

        # Deleting field 'Service.lock'
        db.delete_column('ftp_deploy_service', 'lock')


    models = {
        'ftp_deploy.log': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Log'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payload': ('django.db.models.fields.TextField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ftp_deploy.Service']", 'blank': 'True'}),
            'skip': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'ftp_deploy.notification': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Notification'},
            'commit_user': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deploy_user': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'fail': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'success': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ftp_deploy.service': {
            'Meta': {'object_name': 'Service'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ftp_host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ftp_password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ftp_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ftp_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lock': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ftp_deploy.Notification']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'repo_branch': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'repo_hook': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repo_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'repo_slug_name': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'repo_source': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'default': "'flXcgt3ywDqlzweuPeraGEs7rqGBUk'", 'unique': 'True', 'max_length': '30'}),
            'status': ('django.db.models.fields.BooleanField', [], {}),
            'status_message': ('django.db.models.fields.TextField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ftp_deploy']