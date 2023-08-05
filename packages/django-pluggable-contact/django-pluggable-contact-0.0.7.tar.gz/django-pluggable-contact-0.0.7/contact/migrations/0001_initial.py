# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Topic'
        db.create_table(u'contact_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('display_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'contact', ['Topic'])

        # Adding model 'TopicInbox'
        db.create_table(u'contact_topicinbox', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'inboxes', to=orm['contact.Topic'])),
            ('address', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal(u'contact', ['TopicInbox'])

        # Adding model 'Message'
        db.create_table(u'contact_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'messages', null=True, on_delete=models.SET_NULL, to=orm['contact.Topic'])),
            ('sender', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'contact', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Topic'
        db.delete_table(u'contact_topic')

        # Deleting model 'TopicInbox'
        db.delete_table(u'contact_topicinbox')

        # Deleting model 'Message'
        db.delete_table(u'contact_message')


    models = {
        u'contact.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sender': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
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