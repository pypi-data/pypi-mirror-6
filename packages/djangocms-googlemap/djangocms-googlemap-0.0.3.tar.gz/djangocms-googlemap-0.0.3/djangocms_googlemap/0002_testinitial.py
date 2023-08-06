# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        table_names = connection.introspection.table_names()


        db.rename_table('djangocms_googlemap_googlemap', 'googlemap_googlemap')
        scheme = 'googlemap_googlemap'
        # Get existing columns
        if 'cmsplugin_googlemap' in table_names:
            scheme = 'cmsplugin_googlemap'
        elif 'googlemap_googlemap' in table_names:
            scheme = 'googlemap_googlemap'

        columns = []
        seen_models = connection.introspection.installed_models(table_names)
        for model in seen_models:
            print model
            if model._meta.db_table == scheme:
                columns = [field.column for field in model._meta.fields]

        # Rename tables
        if 'cmsplugin_googlemap' in table_names:
            db.rename_table('cmsplugin_googlemap', 'djangocms_googlemap_googlemap')
        elif 'googlemap_googlemap' in table_names:
            db.rename_table('googlemap_googlemap', 'djangocms_googlemap_googlemap')

        # Check for missing fields from previous migrations
        # (0013_auto__add_field_googlemap_info_window__add_field_googlemap_scrollwheel.py)


        print columns


        # Add missing columns
        if not 'info_window' in columns:
            # Adding field 'GoogleMap.info_window'
            db.add_column(u'djangocms_googlemap_googlemap', 'info_window',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'scrollwheel' in columns:
            # Adding field 'GoogleMap.scrollwheel'
            db.add_column(u'djangocms_googlemap_googlemap', 'scrollwheel',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'double_click_zoom' in columns:
            # Adding field 'GoogleMap.double_click_zoom'
            db.add_column(u'djangocms_googlemap_googlemap', 'double_click_zoom',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'draggable' in columns:
            # Adding field 'GoogleMap.draggable'
            db.add_column(u'djangocms_googlemap_googlemap', 'draggable',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'keyboard_shortcuts' in columns:
            # Adding field 'GoogleMap.keyboard_shortcuts'
            db.add_column(u'djangocms_googlemap_googlemap', 'keyboard_shortcuts',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'pan_control' in columns:
            # Adding field 'GoogleMap.pan_control'
            db.add_column(u'djangocms_googlemap_googlemap', 'pan_control',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'zoom_control' in columns:
            # Adding field 'GoogleMap.zoom_control'
            db.add_column(u'djangocms_googlemap_googlemap', 'zoom_control',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)

        if not 'street_view_control' in columns:
            # Adding field 'GoogleMap.street_view_control'
            db.add_column(u'djangocms_googlemap_googlemap', 'street_view_control',
                          self.gf('django.db.models.fields.BooleanField')(default=True),
                          keep_default=False)


    def backwards(self, orm):
        pass

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
        u'djangocms_googlemap.googlemap': {
            'Meta': {'object_name': 'GoogleMap', '_ormbases': ['cms.CMSPlugin']},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'double_click_zoom': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'draggable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'height': ('django.db.models.fields.CharField', [], {'default': "'400px'", 'max_length': '6'}),
            'info_window': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keyboard_shortcuts': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '6', 'blank': 'True'}),
            'lng': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '6', 'blank': 'True'}),
            'pan_control': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'route_planer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'route_planer_title': ('django.db.models.fields.CharField', [], {'default': "u'Calculate your fastest way to here'", 'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'scrollwheel': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'street_view_control': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.CharField', [], {'default': "'100%'", 'max_length': '6'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'zoom': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '13'}),
            'zoom_control': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['djangocms_googlemap']