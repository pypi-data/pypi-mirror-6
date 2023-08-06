# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

# Safe User import for Django < 1.5
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table(u'wiki_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('current_revision', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='current_set', unique=True, null=True, to=orm['wiki.ArticleRevision'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_articles', null=True, on_delete=models.SET_NULL, to=orm[user_orm_label])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('group_read', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('group_write', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('other_read', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('other_write', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('wiki', ['Article'])

        # Adding model 'ArticleForObject'
        db.create_table(u'wiki_articleforobject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.Article'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='content_type_set_for_articleforobject', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_mptt', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('wiki', ['ArticleForObject'])

        # Adding unique constraint on 'ArticleForObject', fields ['content_type', 'object_id']
        db.create_unique(u'wiki_articleforobject', ['content_type_id', 'object_id'])

        # Adding model 'ArticleRevision'
        db.create_table(u'wiki_articlerevision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision_number', self.gf('django.db.models.fields.IntegerField')()),
            ('user_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('automatic_log', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[user_orm_label], null=True, on_delete=models.SET_NULL, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('previous_revision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.ArticleRevision'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.Article'])),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('wiki', ['ArticleRevision'])

        # Adding unique constraint on 'ArticleRevision', fields ['article', 'revision_number']
        db.create_unique(u'wiki_articlerevision', ['article_id', 'revision_number'])

        # Adding model 'Section'
        db.create_table(u'wiki_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['wiki.Section'])),
            ('article', self.gf('django.db.models.fields.related.OneToOneField')(default=None, related_name='root_node', unique=True, null=True, to=orm['wiki.Article'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, blank=True)),
            ('current_revision', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='current_set', unique=True, null=True, to=orm['wiki.SectionRevision'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owned_sections', null=True, on_delete=models.SET_NULL, to=orm[user_orm_label])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('group_read', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('group_write', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('other_read', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('other_write', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('wiki', ['Section'])

        # Adding unique constraint on 'Section', fields ['parent', 'slug']
        db.create_unique(u'wiki_section', ['parent_id', 'slug'])

        # Adding model 'SectionRevision'
        db.create_table(u'wiki_sectionrevision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision_number', self.gf('django.db.models.fields.IntegerField')()),
            ('user_message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('automatic_log', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[user_orm_label], null=True, on_delete=models.SET_NULL, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('previous_revision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.SectionRevision'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.Section'])),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('wiki', ['SectionRevision'])

        # Adding unique constraint on 'SectionRevision', fields ['section', 'revision_number']
        db.create_unique(u'wiki_sectionrevision', ['section_id', 'revision_number'])

        # Adding model 'URLPath'
        db.create_table(u'wiki_urlpath', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.Article'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['wiki.URLPath'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('wiki', ['URLPath'])

        # Adding unique constraint on 'URLPath', fields ['site', 'parent', 'slug']
        db.create_unique(u'wiki_urlpath', ['site_id', 'parent_id', 'slug'])


    def backwards(self, orm):
        # Removing unique constraint on 'URLPath', fields ['site', 'parent', 'slug']
        db.delete_unique(u'wiki_urlpath', ['site_id', 'parent_id', 'slug'])

        # Removing unique constraint on 'SectionRevision', fields ['section', 'revision_number']
        db.delete_unique(u'wiki_sectionrevision', ['section_id', 'revision_number'])

        # Removing unique constraint on 'Section', fields ['parent', 'slug']
        db.delete_unique(u'wiki_section', ['parent_id', 'slug'])

        # Removing unique constraint on 'ArticleRevision', fields ['article', 'revision_number']
        db.delete_unique(u'wiki_articlerevision', ['article_id', 'revision_number'])

        # Removing unique constraint on 'ArticleForObject', fields ['content_type', 'object_id']
        db.delete_unique(u'wiki_articleforobject', ['content_type_id', 'object_id'])

        # Deleting model 'Article'
        db.delete_table(u'wiki_article')

        # Deleting model 'ArticleForObject'
        db.delete_table(u'wiki_articleforobject')

        # Deleting model 'ArticleRevision'
        db.delete_table(u'wiki_articlerevision')

        # Deleting model 'Section'
        db.delete_table(u'wiki_section')

        # Deleting model 'SectionRevision'
        db.delete_table(u'wiki_sectionrevision')

        # Deleting model 'URLPath'
        db.delete_table(u'wiki_urlpath')


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
        u"%s" % (user_model_label): {
            'Meta': {'object_name': User.__name__},
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'wiki.article': {
            'Meta': {'object_name': 'Article'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_revision': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'current_set'", 'unique': 'True', 'null': 'True', 'to': "orm['wiki.ArticleRevision']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'group_read': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'group_write': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'other_read': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'other_write': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['%s']" % user_orm_label})
        },
        'wiki.articleforobject': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'ArticleForObject'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.Article']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_articleforobject'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_mptt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'wiki.articlerevision': {
            'Meta': {'ordering': "('created',)", 'unique_together': "(('article', 'revision_number'),)", 'object_name': 'ArticleRevision'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.Article']"}),
            'automatic_log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'previous_revision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.ArticleRevision']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s']" % user_orm_label, 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'user_message': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'wiki.section': {
            'Meta': {'unique_together': "(('parent', 'slug'),)", 'object_name': 'Section'},
            'article': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'related_name': "'root_node'", 'unique': 'True', 'null': 'True', 'to': "orm['wiki.Article']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_revision': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'current_set'", 'unique': 'True', 'null': 'True', 'to': "orm['wiki.SectionRevision']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'group_read': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'group_write': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'other_read': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'other_write': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_sections'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['%s']" % user_orm_label}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['wiki.Section']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'wiki.sectionrevision': {
            'Meta': {'ordering': "('created',)", 'unique_together': "(('section', 'revision_number'),)", 'object_name': 'SectionRevision'},
            'automatic_log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'previous_revision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.SectionRevision']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.Section']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s']" % user_orm_label, 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'user_message': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'wiki.urlpath': {
            'Meta': {'unique_together': "(('site', 'parent', 'slug'),)", 'object_name': 'URLPath'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['wiki.URLPath']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['wiki']