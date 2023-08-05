# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DatedValueType.editable'
        db.add_column(u'dated_values_datedvaluetype', 'editable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'DatedValueType.hidden'
        db.add_column(u'dated_values_datedvaluetype', 'hidden',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DatedValueType.editable'
        db.delete_column(u'dated_values_datedvaluetype', 'editable')

        # Deleting field 'DatedValueType.hidden'
        db.delete_column(u'dated_values_datedvaluetype', 'hidden')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dated_values.datedvalue': {
            'Meta': {'ordering': "['date']", 'object_name': 'DatedValue'},
            '_ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dated_values.DatedValueType']"}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '24', 'decimal_places': '8'})
        },
        u'dated_values.datedvaluetype': {
            'Meta': {'object_name': 'DatedValueType'},
            'ctype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'decimal_places': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
