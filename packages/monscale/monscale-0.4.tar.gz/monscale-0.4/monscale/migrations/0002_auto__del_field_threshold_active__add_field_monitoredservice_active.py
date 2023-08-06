# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Threshold.active'
        db.delete_column(u'core_threshold', 'active')

        # Adding field 'MonitoredService.active'
        db.add_column(u'core_monitoredservice', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Threshold.active'
        db.add_column(u'core_threshold', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Deleting field 'MonitoredService.active'
        db.delete_column(u'core_monitoredservice', 'active')


    models = {
        u'core.alarmindicator': {
            'Meta': {'object_name': 'AlarmIndicator'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.MonitoredService']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'core.monitoredservice': {
            'Meta': {'ordering': "['host']", 'object_name': 'MonitoredService'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ScaleAction']"}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'threshold': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Threshold']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.scaleaction': {
            'Meta': {'object_name': 'ScaleAction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'scale_by': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.threshold': {
            'Meta': {'object_name': 'Threshold'},
            'assesment': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'operand': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['core']