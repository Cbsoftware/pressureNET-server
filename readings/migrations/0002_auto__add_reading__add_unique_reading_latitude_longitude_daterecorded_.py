# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Reading'
        db.create_table(u'readings_reading', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('daterecorded', self.gf('django.db.models.fields.IntegerField')()),
            ('reading', self.gf('django.db.models.fields.FloatField')()),
            ('tzoffset', self.gf('django.db.models.fields.IntegerField')()),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'readings', ['Reading'])

        # Adding unique constraint on 'Reading', fields ['latitude', 'longitude', 'daterecorded', 'text']
        db.create_unique(u'readings_reading', ['latitude', 'longitude', 'daterecorded', 'text'])


    def backwards(self, orm):
        # Removing unique constraint on 'Reading', fields ['latitude', 'longitude', 'daterecorded', 'text']
        db.delete_unique(u'readings_reading', ['latitude', 'longitude', 'daterecorded', 'text'])

        # Deleting model 'Reading'
        db.delete_table(u'readings_reading')


    models = {
        u'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'text'),)", 'object_name': 'Reading'},
            'daterecorded': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tzoffset': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['readings']