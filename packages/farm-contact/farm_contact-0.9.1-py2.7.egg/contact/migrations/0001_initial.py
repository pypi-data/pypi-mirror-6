# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EnquiryType'
        db.create_table(u'contact_enquirytype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'contact', ['EnquiryType'])

        # Adding model 'Enquiry'
        db.create_table(u'contact_enquiry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('enquiry_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contact.EnquiryType'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'contact', ['Enquiry'])


    def backwards(self, orm):
        # Deleting model 'EnquiryType'
        db.delete_table(u'contact_enquirytype')

        # Deleting model 'Enquiry'
        db.delete_table(u'contact_enquiry')


    models = {
        u'contact.enquiry': {
            'Meta': {'object_name': 'Enquiry'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'enquiry_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contact.EnquiryType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contact.enquirytype': {
            'Meta': {'object_name': 'EnquiryType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['contact']