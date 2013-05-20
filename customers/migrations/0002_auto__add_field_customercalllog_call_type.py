# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CustomerCallLog.call_type'
        db.add_column('customers_customercalllog', 'call_type',
                      self.gf('django.db.models.fields.CharField')(default='readings', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CustomerCallLog.call_type'
        db.delete_column('customers_customercalllog', 'call_type')


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
            'call_type': ('django.db.models.fields.CharField', [], {'default': "'readings'", 'max_length': '255'}),
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