# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Customer', fields ['company_name', 'contact_name', 'contact_mail']
        db.delete_unique('readings_customer', ['company_name', 'contact_name', 'contact_mail'])

        # Deleting model 'Customer'
        db.delete_table('readings_customer')

        # Deleting model 'CustomerCallLog'
        db.delete_table('readings_customercalllog')


    def backwards(self, orm):
        # Adding model 'Customer'
        db.create_table('readings_customer', (
            ('payment_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('contact_mail', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment_confirmation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('customer_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contact_phone', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
        ))
        db.send_create_signal('readings', ['Customer'])

        # Adding unique constraint on 'Customer', fields ['company_name', 'contact_name', 'contact_mail']
        db.create_unique('readings_customer', ['company_name', 'contact_name', 'contact_mail'])

        # Adding model 'CustomerCallLog'
        db.create_table('readings_customercalllog', (
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['readings.Customer'])),
            ('max_longitude', self.gf('django.db.models.fields.FloatField')()),
            ('min_longitude', self.gf('django.db.models.fields.FloatField')()),
            ('start_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('results_limit', self.gf('django.db.models.fields.IntegerField')()),
            ('processing_time', self.gf('django.db.models.fields.FloatField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('min_latitude', self.gf('django.db.models.fields.FloatField')()),
            ('data_format', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('max_latitude', self.gf('django.db.models.fields.FloatField')()),
            ('since_last_call', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('use_utc', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('results_returned', self.gf('django.db.models.fields.IntegerField')()),
            ('global_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('readings', ['CustomerCallLog'])


    models = {
        'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'user_id'),)", 'object_name': 'Reading'},
            'altitude': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'client_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'location_accuracy': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'observation_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'observation_unit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'provider': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'reading_accuracy': ('django.db.models.fields.FloatField', [], {}),
            'sharing': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'readings.readingsync': {
            'Meta': {'object_name': 'ReadingSync'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processing_time': ('django.db.models.fields.FloatField', [], {}),
            'readings': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['readings']