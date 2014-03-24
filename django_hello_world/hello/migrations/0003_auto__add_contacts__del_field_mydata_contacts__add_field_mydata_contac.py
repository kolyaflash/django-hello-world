# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contacts'
        db.create_table('hello_contacts', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hello.MyData'])),
            ('contact_type', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('hello', ['Contacts'])

        # Deleting field 'MyData.contacts'
        db.delete_column('hello_mydata', 'contacts')

        # Adding field 'MyData.contacts_additional'
        db.add_column('hello_mydata', 'contacts_additional',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)


        # Changing field 'MyData.bio'
        db.alter_column('hello_mydata', 'bio', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):
        # Deleting model 'Contacts'
        db.delete_table('hello_contacts')


        # User chose to not deal with backwards NULL issues for 'MyData.contacts'
        raise RuntimeError("Cannot reverse this migration. 'MyData.contacts' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'MyData.contacts'
        db.add_column('hello_mydata', 'contacts',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)

        # Deleting field 'MyData.contacts_additional'
        db.delete_column('hello_mydata', 'contacts_additional')


        # Changing field 'MyData.bio'
        db.alter_column('hello_mydata', 'bio', self.gf('django.db.models.fields.TextField')(default=1))

    models = {
        'hello.contacts': {
            'Meta': {'object_name': 'Contacts'},
            'contact_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'data': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hello.MyData']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hello.mydata': {
            'Meta': {'object_name': 'MyData'},
            'bio': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'contacts_additional': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['hello']