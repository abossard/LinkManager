# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Site'
        db.create_table('links_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('scheme', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('update_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('inserted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('links', ['Site'])

        # Adding model 'Credential'
        db.create_table('links_credential', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('works', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('update_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('inserted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['links.Site'])),
            ('last_http_code', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_title', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('last_lag', self.gf('django.db.models.fields.IntegerField')(default=999999)),
        ))
        db.send_create_signal('links', ['Credential'])

        # Adding unique constraint on 'Credential', fields ['username', 'password', 'site']
        db.create_unique('links_credential', ['username', 'password', 'site_id'])

        # Adding model 'Proxy'
        db.create_table('links_proxy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70, db_index=True)),
            ('works', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lag', self.gf('django.db.models.fields.IntegerField')(default=999999)),
            ('update_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('inserted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('links', ['Proxy'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Credential', fields ['username', 'password', 'site']
        db.delete_unique('links_credential', ['username', 'password', 'site_id'])

        # Deleting model 'Site'
        db.delete_table('links_site')

        # Deleting model 'Credential'
        db.delete_table('links_credential')

        # Deleting model 'Proxy'
        db.delete_table('links_proxy')


    models = {
        'links.credential': {
            'Meta': {'ordering': "['works', 'last_http_code', 'last_title']", 'unique_together': "(('username', 'password', 'site'),)", 'object_name': 'Credential'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scheme': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'update_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['links']
