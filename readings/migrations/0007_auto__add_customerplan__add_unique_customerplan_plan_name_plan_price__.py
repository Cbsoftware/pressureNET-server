# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CustomerPlan'
        db.create_table('readings_customerplan', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plan_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('plan_price', self.gf('django.db.models.fields.FloatField')()),
            ('global_daily_calls', self.gf('django.db.models.fields.IntegerField')()),
            ('regional_daily_calls', self.gf('django.db.models.fields.IntegerField')()),
            ('region_count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('readings', ['CustomerPlan'])

        # Adding unique constraint on 'CustomerPlan', fields ['plan_name', 'plan_price']
        db.create_unique('readings_customerplan', ['plan_name', 'plan_price'])

        # Adding model 'Customer'
        db.create_table('readings_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contact_mail', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact_phone', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('contact_address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['readings.CustomerPlan'])),
            ('payment_status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('payment_confirmation', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('readings', ['Customer'])

        # Adding unique constraint on 'Customer', fields ['company_name', 'contact_name', 'contact_mail']
        db.create_unique('readings_customer', ['company_name', 'contact_name', 'contact_mail'])

        # Adding model 'CustomerCallLog'
        db.create_table('readings_customercalllog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('min_latitude', self.gf('django.db.models.fields.FloatField')()),
            ('max_latitude', self.gf('django.db.models.fields.FloatField')()),
            ('min_longitude', self.gf('django.db.models.fields.FloatField')()),
            ('max_longitude', self.gf('django.db.models.fields.FloatField')()),
            ('global_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('since_last_call', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('end_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('results_limit', self.gf('django.db.models.fields.IntegerField')()),
            ('data_format', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('use_utc', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processing_time', self.gf('django.db.models.fields.FloatField')()),
            ('results_returned', self.gf('django.db.models.fields.IntegerField')()),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['readings.Customer'])),
        ))
        db.send_create_signal('readings', ['CustomerCallLog'])

        # Adding unique constraint on 'CustomerCallLog', fields ['timestamp', 'api_key']
        db.create_unique('readings_customercalllog', ['timestamp', 'api_key'])


    def backwards(self, orm):
        # Removing unique constraint on 'CustomerCallLog', fields ['timestamp', 'api_key']
        db.delete_unique('readings_customercalllog', ['timestamp', 'api_key'])

        # Removing unique constraint on 'Customer', fields ['company_name', 'contact_name', 'contact_mail']
        db.delete_unique('readings_customer', ['company_name', 'contact_name', 'contact_mail'])

        # Removing unique constraint on 'CustomerPlan', fields ['plan_name', 'plan_price']
        db.delete_unique('readings_customerplan', ['plan_name', 'plan_price'])

        # Deleting model 'CustomerPlan'
        db.delete_table('readings_customerplan')

        # Deleting model 'Customer'
        db.delete_table('readings_customer')

        # Deleting model 'CustomerCallLog'
        db.delete_table('readings_customercalllog')


    models = {
        'readings.customer': {
            'Meta': {'unique_together': "(('company_name', 'contact_name', 'contact_mail'),)", 'object_name': 'Customer'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_mail': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_confirmation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payment_status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['readings.CustomerPlan']"})
        },
        'readings.customercalllog': {
            'Meta': {'unique_together': "(('timestamp', 'api_key'),)", 'object_name': 'CustomerCallLog'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['readings.Customer']"}),
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