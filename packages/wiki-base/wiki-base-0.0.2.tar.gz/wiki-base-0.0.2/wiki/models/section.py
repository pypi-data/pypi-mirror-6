# -*- coding: utf-8 -*-
from mptt.models import TreeForeignKey
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from wiki.conf import settings
from wiki.core import article_markdown, permissions
from wiki.core import compat
from wiki import managers
from wiki.models import BaseRevisionMixin

from mptt.models import MPTTModel


class Section(models.Model):
    objects = managers.PermissionManager()

    current_revision = models.OneToOneField(
        'SectionRevision',
        verbose_name=_(u'current revision'),
        blank=True, null=True, related_name='current_set',
        help_text=_(u'The revision being displayed for this section. '
                    u'If you need to do a roll-back, simply change the value of this field.'),
    )

    deleted = models.BooleanField(
        verbose_name=_(u'deleted'),
        default=False,
    )
    locked = models.BooleanField(
        verbose_name=_(u'locked'),
        default=False,
    )

    created = models.DateTimeField(auto_now_add=True, verbose_name=_(u'created'), )
    modified = models.DateTimeField(auto_now=True, verbose_name=_(u'modified'),
                                    help_text=_(u'Section properties last modified'))

    owner = models.ForeignKey(compat.USER_MODEL, verbose_name=_('owner'),
                              blank=True, null=True, related_name='owned_sections',
                              help_text=_(u'The owner of the section, usually the creator. '
                                          u'The owner always has both read and write access.'),
                              on_delete=models.SET_NULL)

    group = models.ForeignKey(Group, verbose_name=_('group'),
                              blank=True, null=True,
                              help_text=_(u'Like in a UNIX file system, '
                                          u'permissions can be given to a user according to group membership. '
                                          u'Groups are handled through the Django auth system.'),
                              on_delete=models.SET_NULL)

    group_read = models.BooleanField(default=True, verbose_name=_(u'group read access'))
    group_write = models.BooleanField(default=True, verbose_name=_(u'group write access'))
    other_read = models.BooleanField(default=True, verbose_name=_(u'others read access'))
    other_write = models.BooleanField(default=True, verbose_name=_(u'others write access'))

    def can_read(self, user):
        return permissions.can_read(self, user)

    def can_write(self, user):
        return permissions.can_write(self, user)

    def can_delete(self, user):
        return permissions.can_delete(self, user)

    def can_moderate(self, user):
        return permissions.can_moderate(self, user)

    def can_assign(self, user):
        return permissions.can_assign(self, user)

    def add_revision(self, new_revision, save=True):
        """
        Sets the properties of a revision and ensures its the current
        revision.
        """
        assert self.id or save, ('Section.add_revision: Sorry, you cannot add a'
                                 'revision to an section that has not been saved '
                                 'without using save=True')
        if not self.id:
            self.save()
        revisions = self.sectionrevision_set.all()
        try:
            new_revision.revision_number = revisions.latest().revision_number + 1
        except SectionRevision.DoesNotExist:
            new_revision.revision_number = 0
        new_revision.article = self
        new_revision.previous_revision = self.current_revision
        if save:
            new_revision.save()
        self.current_revision = new_revision
        if save:
            self.save()

    def render(self, preview_content=None):
        if not self.current_revision:
            return ""
        if preview_content:
            content = preview_content
        else:
            content = self.current_revision.content
        return mark_safe(article_markdown(content, self))

    def get_cache_key(self):
        return "wiki:section:%d" % (self.current_revision.id if self.current_revision else self.id)

    def get_cached_content(self):
        """Returns cached """
        cache_key = self.get_cache_key()
        cached_content = cache.get(cache_key)
        if cached_content is None:
            cached_content = self.render()
            cache.set(cache_key, cached_content, settings.CACHE_TIMEOUT)
        return cached_content

    def clear_cache(self):
        cache.delete(self.get_cache_key())

    def __unicode__(self):
        if self.current_revision:
            return self.current_revision.title
        obj_name = _(u'Section without content (%(id)d)') % {'id': self.id}
        return unicode(obj_name)

    class Meta:
        app_label = settings.APP_LABEL
        permissions = (
            ("moderate", _(u"Can edit all sections and lock/unlock/restore")),
            ("assign", _(u"Can change ownership of any section")),
            ("grant", _(u"Can assign permissions to other users")),
        )


class SectionRevision(BaseRevisionMixin, models.Model):
    """
    This is where main revision data is stored. To make it easier to
    copy, do NEVER create m2m relationships.

    SectionRevision is directly copied from ArticleRevision.
    """

    section = models.ForeignKey('Section', on_delete=models.CASCADE,
                                verbose_name=_(u'section'))

    # This is where the content goes, with whatever markup language is used
    content = models.TextField(blank=True, verbose_name=_(u'section contents'))

    # This title is automatically set from either the section's title or
    # the last used revision...
    title = models.CharField(max_length=512, verbose_name=_(u'section title'),
                             null=False, blank=False,
                             help_text=_(u'Each section contains a title field that must be filled out, '
                                         u'even if the title has not changed'))

    def __unicode__(self):
        return "%s (%d)" % (self.title, self.revision_number)

    def inherit_predecessor(self, section):
        """
        Inherit certain properties from predecessor because it's very
        convenient. Remember to always call this method before
        setting properties :)"""
        predecessor = section.current_revision
        self.section = predecessor.section
        self.content = predecessor.content
        self.title = predecessor.title

    def save(self, *args, **kwargs):
        if (not self.id
                and not self.previous_revision
                and self.section
                and self.section.current_revision
                and self.section.current_revision != self):

            self.previous_revision = self.section.current_revision

        if not self.revision_number:
            try:
                previous_revision = self.section.sectionrevision_set.latest()
                self.revision_number = previous_revision.revision_number + 1
            except SectionRevision.DoesNotExist:
                self.revision_number = 1

        super(SectionRevision, self).save(*args, **kwargs)

        if not self.section.current_revision:
            # If I'm saved from Django admin, then section.current_revision is me!
            self.section.current_revision = self
            self.section.save()

    class Meta:
        app_label = settings.APP_LABEL
        get_latest_by = 'revision_number'
        ordering = ('created',)
        unique_together = ('section', 'revision_number')


#class SectionTree(MPTTModel):
#    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
#
#    class MPTTMeta:
#        order_insertion_by = ['name']

