# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'MonitoredService.username'
        db.delete_column(u'core_monitoredservice', 'username')

        # Deleting field 'MonitoredService.host'
        db.delete_column(u'core_monitoredservice', 'host')

        # Deleting field 'MonitoredService.password'
        db.delete_column(u'core_monitoredservice', 'password')

        # Adding field 'MonitoredService.data'
        db.add_column(u'core_monitoredservice', 'data',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'MonitoredService.username'
        db.add_column(u'core_monitoredservice', 'username',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'MonitoredService.host'
        db.add_column(u'core_monitoredservice', 'host',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'MonitoredService.password'
        db.add_column(u'core_monitoredservice', 'password',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Deleting field 'MonitoredService.data'
        db.delete_column(u'core_monitoredservice', 'data')


    models = {
        u'core.alarmindicator': {
            'Meta': {'object_name': 'AlarmIndicator'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alarm_indicators'", 'to': u"orm['core.MonitoredService']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'core.monitoredservice': {
            'Meta': {'object_name': 'MonitoredService'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ScaleAction']"}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'threshold': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Threshold']"})
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