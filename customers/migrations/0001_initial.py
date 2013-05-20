# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Customer'
        db.create_table('customers_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('contact_mail', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contact_phone', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('contact_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('customer_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('payment_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('payment_confirmation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('customers', ['Customer'])

        # Adding unique constraint on 'Customer', fields ['company_name', 'contact_name', 'contact_mail']
        db.create_unique('customers_customer', ['company_name', 'contact_name', 'contact_mail'])

        # Adding model 'CustomerCallLog'
        db.create_table('customers_customercalllog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['customers.Customer'])),
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
            ('use_utc', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processing_time', self.gf('django.db.models.fields.FloatField')()),
            ('results_returned', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('customers', ['CustomerCallLog'])


    def backwards(self, orm):
        # Removing unique constraint on 'Customer', fields ['company_name', 'contact_name', 'contact_mail']
        db.delete_unique('customers_customer', ['company_name', 'contact_name', 'contact_mail'])

        # Deleting model 'Customer'
        db.delete_table('customers_customer')

        # Deleting model 'CustomerCallLog'
        db.delete_table('customers_customercalllog')


    models = {
        'customers.customer': {
            'Meta': {'unique_together': "(('company_name', 'contact_name', 'contact_mail'),)", 'object_name': 'Customer'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'contact_mail': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'customer_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_confirmation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'payment_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'customers.customercalllog': {
            'Meta': {'object_name': 'CustomerCallLog'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['customers.Customer']"}),
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
        }
    }

    complete_apps = ['customers']