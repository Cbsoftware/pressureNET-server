# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'CustomerPlan', fields ['plan_name', 'plan_price']
        db.delete_unique('readings_customerplan', ['plan_name', 'plan_price'])

        # Deleting model 'CustomerPlan'
        db.delete_table('readings_customerplan')


        # Changing field 'Customer.payment_status'
        db.alter_column('readings_customer', 'payment_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Customer.customer_type'
        db.alter_column('readings_customer', 'customer_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'Customer.payment_confirmation'
        db.alter_column('readings_customer', 'payment_confirmation', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Customer.contact_address'
        db.alter_column('readings_customer', 'contact_address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Customer.contact_phone'
        db.alter_column('readings_customer', 'contact_phone', self.gf('django.db.models.fields.CharField')(max_length=25, null=True))

    def backwards(self, orm):
        # Adding model 'CustomerPlan'
        db.create_table('readings_customerplan', (
            ('region_count', self.gf('django.db.models.fields.IntegerField')()),
            ('plan_price', self.gf('django.db.models.fields.FloatField')()),
            ('global_daily_calls', self.gf('django.db.models.fields.IntegerField')()),
            ('plan_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('regional_daily_calls', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('readings', ['CustomerPlan'])

        # Adding unique constraint on 'CustomerPlan', fields ['plan_name', 'plan_price']
        db.create_unique('readings_customerplan', ['plan_name', 'plan_price'])


        # Changing field 'Customer.payment_status'
        db.alter_column('readings_customer', 'payment_status', self.gf('django.db.models.fields.CharField')(default='', max_length=20))

        # Changing field 'Customer.customer_type'
        db.alter_column('readings_customer', 'customer_type', self.gf('django.db.models.fields.CharField')(default='', max_length=20))

        # Changing field 'Customer.payment_confirmation'
        db.alter_column('readings_customer', 'payment_confirmation', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Customer.contact_address'
        db.alter_column('readings_customer', 'contact_address', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Customer.contact_phone'
        db.alter_column('readings_customer', 'contact_phone', self.gf('django.db.models.fields.CharField')(default='', max_length=25))

    models = {
        'readings.customer': {
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
        'readings.reading': {
            'Meta': {'unique_together': "(('latitude', 'longitude', 'daterecorded', 'user_id'),)", 'object_name': 'Reading'},
            'client_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'daterecorded': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'location_accuracy': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'reading': ('django.db.models.fields.FloatField', [], {}),
            'reading_accuracy': ('django.db.models.fields.FloatField', [], {}),
            'sharing': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tzoffset': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['readings']