# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GoodsProcessedGroup'
        db.create_table(u'yls_app_goodsprocessedgroup', (
            ('category_name', self.gf('django.db.models.fields.CharField')(max_length=180, primary_key=True, db_index=True)),
            ('product_des', self.gf('django.db.models.fields.CharField')(max_length=1800)),
        ))
        db.send_create_signal(u'yls_app', ['GoodsProcessedGroup'])


    def backwards(self, orm):
        # Deleting model 'GoodsProcessedGroup'
        db.delete_table(u'yls_app_goodsprocessedgroup')


    models = {
        u'yls_app.goods': {
            'Meta': {'object_name': 'Goods'},
            'product_category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'product_html': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True', 'db_index': 'True'}),
            'product_image_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'product_name': ('django.db.models.fields.CharField', [], {'max_length': '800'})
        },
        u'yls_app.goodsprocessed': {
            'Meta': {'object_name': 'GoodsProcessed'},
            'product_category': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'product_des': ('django.db.models.fields.CharField', [], {'max_length': '1800'}),
            'product_html': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True', 'db_index': 'True'})
        },
        u'yls_app.goodsprocessedgroup': {
            'Meta': {'object_name': 'GoodsProcessedGroup'},
            'category_name': ('django.db.models.fields.CharField', [], {'max_length': '180', 'primary_key': 'True', 'db_index': 'True'}),
            'product_des': ('django.db.models.fields.CharField', [], {'max_length': '1800'})
        },
        u'yls_app.stopwords': {
            'Meta': {'object_name': 'StopWords'},
            'word': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        u'yls_app.task': {
            'Meta': {'object_name': 'Task'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infomation': ('django.db.models.fields.CharField', [], {'max_length': '30000'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'task_status': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'task_type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'yls_app.topic': {
            'Meta': {'object_name': 'Topic'},
            'topic_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'topic_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'yls_app.topicword': {
            'Meta': {'object_name': 'TopicWord'},
            'freq': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topic_topic_word'", 'to': u"orm['yls_app.Topic']"}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'yls_app.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'count': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'mcount': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_tweet'", 'to': u"orm['yls_app.WeiboUser']"}),
            'origtext': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True', 'db_index': 'True'})
        },
        u'yls_app.tweettoken': {
            'Meta': {'object_name': 'TweetToken'},
            'tokens': ('django.db.models.fields.CharField', [], {'max_length': '1500'}),
            'tweet': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        u'yls_app.tweetusertoken': {
            'Meta': {'object_name': 'TweetUserToken'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tokens': ('django.db.models.fields.TextField', [], {}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True', 'db_index': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'province_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['yls_app']