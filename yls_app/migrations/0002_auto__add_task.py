# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Task'
        db.create_table(u'yls_app_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('task_status', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('infomation', self.gf('django.db.models.fields.CharField')(max_length=30000)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'yls_app', ['Task'])


    def backwards(self, orm):
        # Deleting model 'Task'
        db.delete_table(u'yls_app_task')


    models = {
        u'yls_app.task': {
            'Meta': {'object_name': 'Task'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infomation': ('django.db.models.fields.CharField', [], {'max_length': '30000'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'task_status': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'task_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['yls_app']