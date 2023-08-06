# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProductCategoryAuditLogEntry'
        db.create_table(u'store_productcategoryauditlogentry', (
            ('created_by', self.gf('audit_log.models.fields.CreatingUserField')(related_name='_auditlog_created_categories', to=orm['auth.User'])),
            ('modified_by', self.gf('audit_log.models.fields.LastUserField')(related_name='_auditlog_modified_categories', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_productcategory_audit_log_entry', to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'store', ['ProductCategoryAuditLogEntry'])

        # Adding model 'ProductCategory'
        db.create_table(u'store_productcategory', (
            ('created_by', self.gf('audit_log.models.fields.CreatingUserField')(related_name='created_categories', to=orm['auth.User'])),
            ('modified_by', self.gf('audit_log.models.fields.LastUserField')(related_name='modified_categories', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'store', ['ProductCategory'])

        # Adding model 'ProductAuditLogEntry'
        db.create_table(u'store_productauditlogentry', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.ProductCategory'])),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_product_audit_log_entry', to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'store', ['ProductAuditLogEntry'])

        # Adding model 'Product'
        db.create_table(u'store_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.ProductCategory'])),
        ))
        db.send_create_signal(u'store', ['Product'])

        # Adding model 'ProductRating'
        db.create_table(u'store_productrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('audit_log.models.fields.LastUserField')(to=orm['auth.User'])),
            ('session', self.gf('audit_log.models.fields.LastSessionKeyField')(max_length=40, null=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Product'])),
            ('rating', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'store', ['ProductRating'])

        # Adding model 'SaleInvoiceAuditLogEntry'
        db.create_table(u'store_saleinvoiceauditlogentry', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_saleinvoice_audit_log_entry', to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'store', ['SaleInvoiceAuditLogEntry'])

        # Adding model 'SaleInvoice'
        db.create_table(u'store_saleinvoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'store', ['SaleInvoice'])

        # Adding model 'SoldQuantityAuditLogEntry'
        db.create_table(u'store_soldquantityauditlogentry', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Product'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('sale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.SaleInvoice'])),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_soldquantity_audit_log_entry', to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'store', ['SoldQuantityAuditLogEntry'])

        # Adding model 'SoldQuantity'
        db.create_table(u'store_soldquantity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.Product'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('sale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store.SaleInvoice'])),
        ))
        db.send_create_signal(u'store', ['SoldQuantity'])

        # Adding model 'Widget'
        db.create_table(u'store_widget', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'store', ['Widget'])

        # Adding model 'ExtremeWidgetAuditLogEntry'
        db.create_table(u'store_extremewidgetauditlogentry', (
            (u'widget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['store.Widget'])),
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('special_power', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_extremewidget_audit_log_entry', to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'store', ['ExtremeWidgetAuditLogEntry'])

        # Adding model 'ExtremeWidget'
        db.create_table(u'store_extremewidget', (
            (u'widget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['store.Widget'], unique=True, primary_key=True)),
            ('special_power', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'store', ['ExtremeWidget'])


    def backwards(self, orm):
        # Deleting model 'ProductCategoryAuditLogEntry'
        db.delete_table(u'store_productcategoryauditlogentry')

        # Deleting model 'ProductCategory'
        db.delete_table(u'store_productcategory')

        # Deleting model 'ProductAuditLogEntry'
        db.delete_table(u'store_productauditlogentry')

        # Deleting model 'Product'
        db.delete_table(u'store_product')

        # Deleting model 'ProductRating'
        db.delete_table(u'store_productrating')

        # Deleting model 'SaleInvoiceAuditLogEntry'
        db.delete_table(u'store_saleinvoiceauditlogentry')

        # Deleting model 'SaleInvoice'
        db.delete_table(u'store_saleinvoice')

        # Deleting model 'SoldQuantityAuditLogEntry'
        db.delete_table(u'store_soldquantityauditlogentry')

        # Deleting model 'SoldQuantity'
        db.delete_table(u'store_soldquantity')

        # Deleting model 'Widget'
        db.delete_table(u'store_widget')

        # Deleting model 'ExtremeWidgetAuditLogEntry'
        db.delete_table(u'store_extremewidgetauditlogentry')

        # Deleting model 'ExtremeWidget'
        db.delete_table(u'store_extremewidget')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'store.extremewidget': {
            'Meta': {'object_name': 'ExtremeWidget', '_ormbases': [u'store.Widget']},
            'special_power': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['store.Widget']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'store.extremewidgetauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'ExtremeWidgetAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_extremewidget_audit_log_entry'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'special_power': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'widget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['store.Widget']"})
        },
        u'store.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.ProductCategory']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'store.productauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'ProductAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_product_audit_log_entry'", 'to': u"orm['auth.User']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.ProductCategory']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'store.productcategory': {
            'Meta': {'object_name': 'ProductCategory'},
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'created_categories'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'modified_categories'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'primary_key': 'True'})
        },
        u'store.productcategoryauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'ProductCategoryAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_productcategory_audit_log_entry'", 'to': u"orm['auth.User']"}),
            'created_by': ('audit_log.models.fields.CreatingUserField', [], {'related_name': "'_auditlog_created_categories'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'modified_by': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_auditlog_modified_categories'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'})
        },
        u'store.productrating': {
            'Meta': {'object_name': 'ProductRating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Product']"}),
            'rating': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'session': ('audit_log.models.fields.LastSessionKeyField', [], {'max_length': '40', 'null': 'True'}),
            'user': ('audit_log.models.fields.LastUserField', [], {'to': u"orm['auth.User']"})
        },
        u'store.saleinvoice': {
            'Meta': {'object_name': 'SaleInvoice'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'store.saleinvoiceauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'SaleInvoiceAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_saleinvoice_audit_log_entry'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'})
        },
        u'store.soldquantity': {
            'Meta': {'object_name': 'SoldQuantity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'sale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.SaleInvoice']"})
        },
        u'store.soldquantityauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'SoldQuantityAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_soldquantity_audit_log_entry'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'sale': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store.SaleInvoice']"})
        },
        u'store.widget': {
            'Meta': {'object_name': 'Widget'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['store']