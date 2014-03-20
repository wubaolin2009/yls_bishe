# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WeiboUser'
        db.create_table(u'yls_app_weibouser', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
            ('nick', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('head', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.IntegerField')()),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('province_code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('city_code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('fansnum', self.gf('django.db.models.fields.IntegerField')()),
            ('idolnum', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'yls_app', ['WeiboUser'])

        # Adding model 'UserIdolList'
        db.create_table(u'yls_app_useridollist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_idol_list', to=orm['yls_app.WeiboUser'])),
            ('idol_name', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_idol_name', to=orm['yls_app.WeiboUser'])),
        ))
        db.send_create_signal(u'yls_app', ['UserIdolList'])

        # Adding model 'Tweet'
        db.create_table(u'yls_app_tweet', (
            ('tweet_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('origtext', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('count', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('mcount', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('image', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_tweet', to=orm['yls_app.WeiboUser'])),
        ))
        db.send_create_signal(u'yls_app', ['Tweet'])


    def backwards(self, orm):
        # Deleting model 'WeiboUser'
        db.delete_table(u'yls_app_weibouser')

        # Deleting model 'UserIdolList'
        db.delete_table(u'yls_app_useridollist')

        # Deleting model 'Tweet'
        db.delete_table(u'yls_app_tweet')


    models = {
        u'yls_app.task': {
            'Meta': {'object_name': 'Task'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infomation': ('django.db.models.fields.CharField', [], {'max_length': '30000'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'task_status': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'task_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'yls_app.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'count': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mcount': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_tweet'", 'to': u"orm['yls_app.WeiboUser']"}),
            'origtext': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'tweet_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'yls_app.useridollist': {
            'Meta': {'object_name': 'UserIdolList'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idol_name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_idol_name'", 'to': u"orm['yls_app.WeiboUser']"}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_idol_list'", 'to': u"orm['yls_app.WeiboUser']"})
        },
        u'yls_app.weibouser': {
            'Meta': {'object_name': 'WeiboUser'},
            'city_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'fansnum': ('django.db.models.fields.IntegerField', [], {}),
            'head': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'idolnum': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'province_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['yls_app']