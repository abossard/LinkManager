# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Credential.keeper'
        db.add_column('links_credential', 'keeper', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Site.ignore'
        db.add_column('links_site', 'ignore', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Credential.keeper'
        db.delete_column('links_credential', 'keeper')

        # Deleting field 'Site.ignore'
        db.delete_column('links_site', 'ignore')


    models = {
        'links.credential': {
            'Meta': {'ordering': "['-works', 'last_http_code', 'last_title']", 'unique_together': "(('username', 'password', 'site'),)", 'object_name': 'Credential'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'keeper': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_http_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_lag': ('django.db.models.fields.IntegerField', [], {'default': '999999'}),
            'last_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['links.Site']"}),
            'update_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'works': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'links.proxy': {
            'Meta': {'ordering': "['-works', 'lag']", 'object_name': 'Proxy'},
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'lag': ('django.db.models.fields.IntegerField', [], {'default': '999999'}),
            'update_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'works': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'links.site': {
            'Meta': {'ordering': "['hostname', 'path']", 'object_name': 'Site'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inserted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scheme': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'update_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['links']
