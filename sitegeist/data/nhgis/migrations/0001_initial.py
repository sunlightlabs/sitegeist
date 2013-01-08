# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tract'
        db.create_table('nhgis_tract', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('tract', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('units', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('nhgis', ['Tract'])


    def backwards(self, orm):
        # Deleting model 'Tract'
        db.delete_table('nhgis_tract')


    models = {
        'nhgis.tract': {
            'Meta': {'ordering': "('state', 'county', 'tract')", 'object_name': 'Tract'},
            'county': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tract': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'units': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        }
    }

    complete_apps = ['nhgis']