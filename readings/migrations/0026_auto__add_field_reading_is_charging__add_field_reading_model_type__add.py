# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Reading.is_charging'
        db.add_column(u'readings_reading', 'is_charging',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Reading.model_type'
        db.add_column(u'readings_reading', 'model_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Reading.version_number'
        db.add_column(u'readings_reading', 'version_number',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'Reading.package_name'
        db.add_column(u'readings_reading', 'package_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Reading.is_charging'
        db.delete_column(u'readings_reading', 'is_charging')

        # Deleting field 'Reading.model_type'
        db.delete_column(u'readings_reading', 'model_type')

        # Deleting field 'Reading.version_number'
        db.delete_column(u'readings_reading', 'version_number')

        # Deleting field 'Reading.package_name'
        db.delete_column(u'readings_reading', 'package_name')


    models = {
        u'readings.condition': {
            'Meta': {'object_name': 'Condition'},
            'accuracy': ('django.db.models.fields.FloatField', [], {}),
            'altitude': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'client_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cloud_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'fog_thickness': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'general_condition': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'precipitation_amount': ('django.db.models.fields.FloatField', [], {}),
            'precipitation_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'precipitation_unit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'provider': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'sharing': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'thunderstorm_intensity': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'windy': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'readings.conditionfilter': {
            'Meta': {'object_name': 'ConditionFilter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'readings.reading': {
            'Meta': {'object_name': 'Reading'},
            'altitude': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'client_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_charging': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'location_accuracy': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'model_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'observation_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'observation_unit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'package_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'provider': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'reading_accuracy': ('django.db.models.fields.FloatField', [], {}),
            'sharing': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'version_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'})
        },
        u'readings.readingsync': {
            'Meta': {'object_name': 'ReadingSync'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processing_time': ('django.db.models.fields.FloatField', [], {}),
            'readings': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['readings']