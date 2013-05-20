# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Reading', fields ['latitude', 'text', 'daterecorded', 'longitude']
        db.delete_unique(u'readings_reading', ['latitude', 'text', 'daterecorded', 'longitude'])

        # Deleting field 'Reading.text'
        db.delete_column(u'readings_reading', 'text')

        # Adding field 'Reading.user_id'
        db.add_column(u'readings_reading', 'user_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding unique constraint on 'Reading', fields ['latitude', 'user_id', 'daterecorded', 'longitude']
        db.create_unique(u'readings_reading', ['latitude', 'user_id', 'daterecorded', 'longitude'])


    def backwards(self, orm):
        # Removing unique constraint on 'Reading', fields ['latitude', 'user_id', 'daterecorded', 'longitude']
        db.delete_unique(u'readings_reading', ['latitude', 'user_id', 'daterecorded', 'longitude'])

        # Adding field 'Reading.text'
        db.add_column(u'readings_reading', 'text',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Deleting field 'Reading.user_id'
        db.delete_column(u'readings_reading', 'user_id')

        # Adding unique constraint on 'Reading', fields ['latitude', 'text', 'daterecorded', 'longitude']
        db.create_unique(u'readings_reading', ['latitude', 'text', 'daterecorded', 'longitude'])


    models = {
        u'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'user_id'),)", 'object_name': 'Reading'},
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['readings']