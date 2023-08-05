# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DatedValue'
        db.create_table(u'dated_values_datedvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_ctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dated_values.DatedValueType'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=24, decimal_places=8)),
        ))
        db.send_create_signal(u'dated_values', ['DatedValue'])

        # Adding model 'DatedValueTypeTranslation'
        db.create_table(u'dated_values_datedvaluetype_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['dated_values.DatedValueType'])),
        ))
        db.send_create_signal(u'dated_values', ['DatedValueTypeTranslation'])

        # Adding unique constraint on 'DatedValueTypeTranslation', fields ['language_code', 'master']
        db.create_unique(u'dated_values_datedvaluetype_translation', ['language_code', 'master_id'])

        # Adding model 'DatedValueType'
        db.create_table(u'dated_values_datedvaluetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], unique=True)),
            ('decimal_places', self.gf('django.db.models.fields.PositiveIntegerField')(default=2)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
        ))
        db.send_create_signal(u'dated_values', ['DatedValueType'])


    def backwards(self, orm):
        # Removing unique constraint on 'DatedValueTypeTranslation', fields ['language_code', 'master']
        db.delete_unique(u'dated_values_datedvaluetype_translation', ['language_code', 'master_id'])

        # Deleting model 'DatedValue'
        db.delete_table(u'dated_values_datedvalue')

        # Deleting model 'DatedValueTypeTranslation'
        db.delete_table(u'dated_values_datedvaluetype_translation')

        # Deleting model 'DatedValueType'
        db.delete_table(u'dated_values_datedvaluetype')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dated_values.datedvalue': {
            'Meta': {'object_name': 'DatedValue'},
            '_ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dated_values.DatedValueType']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '24', 'decimal_places': '8'})
        },
        u'dated_values.datedvaluetype': {
            'Meta': {'object_name': 'DatedValueType'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'unique': 'True'}),
            'decimal_places': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'dated_values.datedvaluetypetranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'DatedValueTypeTranslation', 'db_table': "u'dated_values_datedvaluetype_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['dated_values.DatedValueType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['dated_values']
