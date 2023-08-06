# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Setting'
        db.create_table('settings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('settings', ['Setting'])


    def backwards(self, orm):
        # Deleting model 'Setting'
        db.delete_table('settings')


    models = {
        'settings.setting': {
            'Meta': {'object_name': 'Setting', 'db_table': "'settings'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['settings']
