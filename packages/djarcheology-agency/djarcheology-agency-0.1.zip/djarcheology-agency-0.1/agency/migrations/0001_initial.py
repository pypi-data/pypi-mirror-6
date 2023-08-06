# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Agent'
        db.create_table(u'agency_agent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_agency.agent_set', null=True, to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal(u'agency', ['Agent'])

        # Adding model 'Person'
        db.create_table(u'agency_person', (
            (u'agent_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['agency.Agent'], unique=True, primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'agency', ['Person'])

        # Adding model 'Organization'
        db.create_table(u'agency_organization', (
            (u'agent_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['agency.Agent'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'agency', ['Organization'])


    def backwards(self, orm):
        # Deleting model 'Agent'
        db.delete_table(u'agency_agent')

        # Deleting model 'Person'
        db.delete_table(u'agency_person')

        # Deleting model 'Organization'
        db.delete_table(u'agency_organization')


    models = {
        u'agency.agent': {
            'Meta': {'object_name': 'Agent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_agency.agent_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'agency.organization': {
            'Meta': {'object_name': 'Organization', '_ormbases': [u'agency.Agent']},
            u'agent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['agency.Agent']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'agency.person': {
            'Meta': {'object_name': 'Person', '_ormbases': [u'agency.Agent']},
            u'agent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['agency.Agent']", 'unique': 'True', 'primary_key': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['agency']