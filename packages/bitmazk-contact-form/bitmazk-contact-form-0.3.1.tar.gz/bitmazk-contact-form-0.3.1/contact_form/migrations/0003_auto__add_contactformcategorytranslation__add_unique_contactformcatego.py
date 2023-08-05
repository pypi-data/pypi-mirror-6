# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContactFormCategoryTranslation'
        db.create_table(u'contact_form_contactformcategory_translation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('language_code', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='translations', null=True, to=orm['contact_form.ContactFormCategory'])),
        ))
        db.send_create_signal(u'contact_form', ['ContactFormCategoryTranslation'])

        # Adding unique constraint on 'ContactFormCategoryTranslation', fields ['language_code', 'master']
        db.create_unique(u'contact_form_contactformcategory_translation', ['language_code', 'master_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ContactFormCategoryTranslation', fields ['language_code', 'master']
        db.delete_unique(u'contact_form_contactformcategory_translation', ['language_code', 'master_id'])

        # Deleting model 'ContactFormCategoryTranslation'
        db.delete_table(u'contact_form_contactformcategory_translation')


    models = {
        u'contact_form.contactformcategory': {
            'Meta': {'object_name': 'ContactFormCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
        },
        u'contact_form.contactformcategorytranslation': {
            'Meta': {'unique_together': "[('language_code', 'master')]", 'object_name': 'ContactFormCategoryTranslation', 'db_table': "u'contact_form_contactformcategory_translation'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'translations'", 'null': 'True', 'to': u"orm['contact_form.ContactFormCategory']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'contact_form.contactformcategorytranslationrenamed': {
            'Meta': {'object_name': 'ContactFormCategoryTranslationRenamed'},
            'contact_form_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contact_form.ContactFormCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['contact_form']