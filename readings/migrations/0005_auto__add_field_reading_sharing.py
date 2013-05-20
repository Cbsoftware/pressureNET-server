# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Reading.sharing'
        db.add_column('readings_reading', 'sharing',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Reading.sharing'
        db.delete_column('readings_reading', 'sharing')


    models = {
        'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'user_id'),)", 'object_name': 'Reading'},
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'sharing': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['readings']