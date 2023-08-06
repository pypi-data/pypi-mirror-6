# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Accordion'
        db.create_table(u'cmsplugin_accordion_accordion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'cmsplugin_accordion', ['Accordion'])

        # Adding model 'AccordionRow'
        db.create_table(u'cmsplugin_accordion_accordionrow', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('accordion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='accordion_rows', to=orm['cmsplugin_accordion.Accordion'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cms.Placeholder'], null=True)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_accordion', ['AccordionRow'])

        # Adding model 'AccordionPluginModel'
        db.create_table(u'cmsplugin_accordionpluginmodel', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('accordion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_accordion.Accordion'])),
        ))
        db.send_create_signal(u'cmsplugin_accordion', ['AccordionPluginModel'])


    def backwards(self, orm):
        # Deleting model 'Accordion'
        db.delete_table(u'cmsplugin_accordion_accordion')

        # Deleting model 'AccordionRow'
        db.delete_table(u'cmsplugin_accordion_accordionrow')

        # Deleting model 'AccordionPluginModel'
        db.delete_table(u'cmsplugin_accordionpluginmodel')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'cmsplugin_accordion.accordion': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Accordion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'cmsplugin_accordion.accordionpluginmodel': {
            'Meta': {'object_name': 'AccordionPluginModel', 'db_table': "u'cmsplugin_accordionpluginmodel'", '_ormbases': ['cms.CMSPlugin']},
            'accordion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_accordion.Accordion']"}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'cmsplugin_accordion.accordionrow': {
            'Meta': {'ordering': "('accordion__name', 'position', 'title')", 'object_name': 'AccordionRow'},
            'accordion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accordion_rows'", 'to': u"orm['cmsplugin_accordion.Accordion']"}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['cmsplugin_accordion']