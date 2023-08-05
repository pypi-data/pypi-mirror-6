# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Action', fields ['urlname']
        db.create_index('notifications_action', ['urlname'])

        # Adding index on 'Action', fields ['order']
        db.create_index('notifications_action', ['order'])

        # Adding index on 'ContextVariable', fields ['object_id']
        db.create_index('notifications_contextvariable', ['object_id'])

        # Adding index on 'ContextVariable', fields ['name']
        db.create_index('notifications_contextvariable', ['name'])

        # Adding index on 'Notification', fields ['kind']
        db.create_index('notifications_notification', ['kind'])

        # Adding index on 'Notification', fields ['module']
        db.create_index('notifications_notification', ['module'])

        # Adding index on 'Notification', fields ['happened']
        db.create_index('notifications_notification', ['happened'])


    def backwards(self, orm):
        # Removing index on 'Notification', fields ['happened']
        db.delete_index('notifications_notification', ['happened'])

        # Removing index on 'Notification', fields ['module']
        db.delete_index('notifications_notification', ['module'])

        # Removing index on 'Notification', fields ['kind']
        db.delete_index('notifications_notification', ['kind'])

        # Removing index on 'ContextVariable', fields ['name']
        db.delete_index('notifications_contextvariable', ['name'])

        # Removing index on 'ContextVariable', fields ['object_id']
        db.delete_index('notifications_contextvariable', ['object_id'])

        # Removing index on 'Action', fields ['order']
        db.delete_index('notifications_action', ['order'])

        # Removing index on 'Action', fields ['urlname']
        db.delete_index('notifications_action', ['urlname'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'notifications.action': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Action'},
            'args': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kwargs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['notifications.Notification']"}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'urlname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'notifications.contextvariable': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('notification', 'name'),)", 'object_name': 'ContextVariable'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notification_contexts'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'context'", 'to': "orm['notifications.Notification']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'notifications.deliverypreference': {
            'Meta': {'unique_together': "(('user', 'module', 'kind'),)", 'object_name': 'DeliveryPreference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'methods': ('django.db.models.fields.TextField', [], {'default': '\'["email"]\''}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notification_preferences'", 'to': "orm['auth.User']"})
        },
        'notifications.notification': {
            'Meta': {'ordering': "('-happened',)", 'object_name': 'Notification'},
            'happened': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'relevant_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['notifications']