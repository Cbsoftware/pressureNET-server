# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Reading.daterecorded'
        db.alter_column(u'readings_reading', 'daterecorded', self.gf('django.db.models.fields.BigIntegerField')())

        # Changing field 'Reading.tzoffset'
        db.alter_column(u'readings_reading', 'tzoffset', self.gf('django.db.models.fields.BigIntegerField')())

    def backwards(self, orm):

        # Changing field 'Reading.daterecorded'
        db.alter_column(u'readings_reading', 'daterecorded', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Reading.tzoffset'
        db.alter_column(u'readings_reading', 'tzoffset', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'text'),)", 'object_name': 'Reading'},
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['readings']