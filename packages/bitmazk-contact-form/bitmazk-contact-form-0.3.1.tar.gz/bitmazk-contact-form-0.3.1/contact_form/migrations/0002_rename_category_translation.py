# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table(u'contact_form_contactformcategorytranslation', u'contact_form_contactformcategorytranslationrenamed')

    def backwards(self, orm):
        db.rename_table(u'contact_form_contactformcategorytranslationrenamed', u'contact_form_contactformcategorytranslation')

    models = {
        u'contact_form.contactformcategory': {
            'Meta': {'object_name': 'ContactFormCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
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
