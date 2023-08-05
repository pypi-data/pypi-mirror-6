# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Account.accountnr'
        db.alter_column(u'homebanking_account', 'accountnr', self.gf('django.db.models.fields.BigIntegerField')())

    def backwards(self, orm):

        # Changing field 'Account.accountnr'
        db.alter_column(u'homebanking_account', 'accountnr', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'homebanking.account': {
            'Meta': {'object_name': 'Account'},
            'accountnr': ('django.db.models.fields.BigIntegerField', [], {}),
            'agreement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['homebanking.Agreement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'regnr': ('django.db.models.fields.IntegerField', [], {})
        },
        u'homebanking.agreement': {
            'Meta': {'object_name': 'Agreement'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['homebanking.UserAccount']"}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'homebanking.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'homebanking.categorymatcher': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CategoryMatcher'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['homebanking.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'regex': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'homebanking.entry': {
            'Meta': {'object_name': 'Entry'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['homebanking.Account']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'balance': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['homebanking.Category']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subindex': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'homebanking.useraccount': {
            'Meta': {'object_name': 'UserAccount'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['homebanking']