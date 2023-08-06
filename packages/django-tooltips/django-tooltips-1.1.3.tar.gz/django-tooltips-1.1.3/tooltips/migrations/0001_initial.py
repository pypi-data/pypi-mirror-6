# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tooltip'
        db.create_table(u'tooltips_tooltip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('selector', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'tooltips', ['Tooltip'])


    def backwards(self, orm):
        # Deleting model 'Tooltip'
        db.delete_table(u'tooltips_tooltip')


    models = {
        u'tooltips.tooltip': {
            'Meta': {'object_name': 'Tooltip'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selector': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['tooltips']