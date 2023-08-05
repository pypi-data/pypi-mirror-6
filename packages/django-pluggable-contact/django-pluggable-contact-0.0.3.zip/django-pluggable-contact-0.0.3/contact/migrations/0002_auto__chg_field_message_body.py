# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Message.body'
        db.alter_column(u'contact_message', 'body', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Message.body'
        db.alter_column(u'contact_message', 'body', self.gf('django.db.models.fields.TextField')(default='1234567890'))

    models = {
        u'contact.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sender': ('django.db.models.fields.EmailField', [], {'default': "'webmaster@localhost'", 'max_length': '75'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'messages'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['contact.Topic']"})
        },
        u'contact.topic': {
            'Meta': {'object_name': 'Topic'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        u'contact.topicinbox': {
            'Meta': {'object_name': 'TopicInbox'},
            'address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'inboxes'", 'to': u"orm['contact.Topic']"})
        }
    }

    complete_apps = ['contact']