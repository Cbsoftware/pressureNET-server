# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Customer.customer_type'
        db.add_column('readings_customer', 'customer_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Customer.customer_type'
        db.delete_column('readings_customer', 'customer_type')


    models = {
        'readings.customer': {
            'Meta': {'unique_together': "(('company_name', 'contact_name', 'contact_mail'),)", 'object_name': 'Customer'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_mail': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'customer_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_confirmation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payment_status': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'readings.customercalllog': {
            'Meta': {'unique_together': "(('timestamp', 'api_key'),)", 'object_name': 'CustomerCallLog'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data_format': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'end_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'global_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_latitude': ('django.db.models.fields.FloatField', [], {}),
            'max_longitude': ('django.db.models.fields.FloatField', [], {}),
            'min_latitude': ('django.db.models.fields.FloatField', [], {}),
            'min_longitude': ('django.db.models.fields.FloatField', [], {}),
            'processing_time': ('django.db.models.fields.FloatField', [], {}),
            'results_limit': ('django.db.models.fields.IntegerField', [], {}),
            'results_returned': ('django.db.models.fields.IntegerField', [], {}),
            'since_last_call': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'use_utc': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'readings.customerplan': {
            'Meta': {'unique_together': "(('plan_name', 'plan_price'),)", 'object_name': 'CustomerPlan'},
            'global_daily_calls': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'plan_price': ('django.db.models.fields.FloatField', [], {}),
            'region_count': ('django.db.models.fields.IntegerField', [], {}),
            'regional_daily_calls': ('django.db.models.fields.IntegerField', [], {})
        },
        'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'user_id'),)", 'object_name': 'Reading'},
            'client_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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