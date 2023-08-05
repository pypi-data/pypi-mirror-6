#!/usr/bin/env python
# encoding: utf-8

"""
hstore_flattenfields.models
-------------

The Models file where places all the stored classes
used in hstore_flattenfields application.

:copyright: 2013, multmeio (http://www.multmeio.com.br)
:author: 2013, Iuri Diniz <iuridiniz@gmail.com>
:license: BSD, see LICENSE for more details.
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from django_orm.postgresql import hstore
from django_extensions.db.fields import AutoSlugField

from db.base import (
    HStoreModel,
    HStoreGroupedModel,
    HStoreM2MGroupedModel,
)
from hstore_flattenfields.utils import (
    single_list_to_tuple,
    FIELD_TYPES,
    FIELD_TYPES_WITHOUT_BLANK_OPTION,
)
from hstore_flattenfields.signals import *


# Setup the "class Meta:" flattenfields custom configs
models.options.DEFAULT_NAMES += (
    'hstore_related_field',
)

class DynamicFieldGroup(models.Model):
    """
    Class context to fields in the use case.
    This has to be implemented on main app, and related to
    class HstoreModel that contains ``_dfields``.

    :param name: The name of the Group.
    :param slug: Auto-slug which was generated using the ``name`` as a seed.
    :param description: The text description about what this Group means in your logic.

    >>> group = DynamicFieldGroup.objects.create(name="Test Group")
    >>> group.slug
    u'test_group'

    >>> group.name = "New Group"
    >>> group.save()
    >>> group.slug
    u'new_group'
    """
    name = models.CharField(max_length=80, null=False, verbose_name=_('Name'))
    slug = AutoSlugField(populate_from='name', separator='_', max_length=100, unique=True, overwrite=True)
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))

    class Meta:
        verbose_name = _('Dynamic Field Group')
        verbose_name_plural = _('Dynamic Field Groups')

    def __unicode__(self):
        """
        Returns a pretty representation of this object.

        >>> group = DynamicFieldGroup.objects.create(name="Test Group")
        >>> unicode(group)
        u'Test Group'
        """
        return u"%s" % self.name

    @property
    def fields(self):
        """
        Returns all the related ``DynamicField`` instances from cache.

        >>> DynamicField.objects.all().delete()
        >>> group = DynamicFieldGroup.objects.create(name="Test Group")
        >>> DynamicField.objects.create(refer="Something", group=group, name="something_age", verbose_name=u"Age")
        <DynamicField: Age>
        >>> group.fields
        [<DynamicField: Age>]
        """
        return DynamicField.objects.filter(models.Q(group=self) | models.Q(group=None))


class ContentPane(models.Model):
    """
    Class to contains fields reproduced into TABs, DIVs,... on templates.

    :param name: The name of the ``ContentPane``.
    :param slug: Auto-slug which was generated using the ``name`` as a seed.
    :param order: The 0-indexed order which the ``ContentPane`` is places inside the ``Form``.
    :param content_type: The ``ContentType`` which the ``ContentPane`` will be shown.
    :param group: The ``DynamicFieldGroup`` instance which the ``ContentPane`` is owned.

    >>> content_pane = ContentPane.objects.create(name="Test Content Pane")
    >>> content_pane.slug
    u'test_content_pane'
    """
    name = models.CharField(max_length=80, null=False, verbose_name=_('Name'))
    order = models.IntegerField(null=False, blank=False, default=0, verbose_name=_('Order'))
    slug = AutoSlugField(populate_from='name', separator='_',max_length=100, unique=True, overwrite=True)

    # relations
    content_type = models.ForeignKey(ContentType, null=True, blank=True, related_name='content_panes')
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name='content_panes', verbose_name=_("Groups"))

    class Meta:
        verbose_name = _('Content Pane')
        verbose_name_plural = _('Content Panes')
        ordering = ['order', 'slug']

    def __unicode__(self):
        """
        Returns a pretty representation of this object.

        >>> content_pane = ContentPane.objects.create(name="Test Content Pane")
        >>> unicode(content_pane)
        u'Test Content Pane'
        """
        return u"%s" % self.name

    @property
    def fields(self):
        """
        Returns all the related ``DynamicField`` instances from cache.

        >>> content_pane = ContentPane.objects.create(name="Test Content Pane")
        >>> DynamicField.objects.create(refer="MyModel", content_pane=content_pane, name="my_model_age", verbose_name=u"Age")
        <DynamicField: Age>
        >>> DynamicField.objects.create(refer="MyModel", name="my_model_foobar", verbose_name=u"Foobar")
        <DynamicField: Foobar>
        >>> content_pane.fields
        [<DynamicField: Age>]
        """
        return self.dynamic_fields.order_by('order')

    @property
    def is_generic(self):
        """
        Return a boolean value if this ``ContentPane`` is Generic,
        that means if this ``ContentPane`` will be shown everywhere, like
        in forms, views...

        >>> group = DynamicFieldGroup.objects.create(name="Test Group Generic")
        >>> content_pane = ContentPane.objects.create(name="Test Content Pane Generic")
        >>> content_pane.is_generic
        True
        >>> content_pane2 = ContentPane.objects.create(name="Test Content Pane Not Generic", group=group)
        >>> content_pane2.is_generic
        False

        """
        return not self.group


class DynamicField(models.Model):
    """
    Created to represent the Django Model's field information,
    we use him to fill the Field instances when the ``refer``
    instances will be build.

    :param refer: The name of the Model of the ``DynamicField``.
    :param name: The name of the ``DynamicField``.
    :param verbose_name: The Verbose Name of the ``DynamicField``.
    :param order: The 0-indexed order which the ``DynamicField`` is places inside the ``Form``.
    :param content_type: The ``ContentType`` which the ``ContentPane`` will be shown.
    :param group: The ``DynamicFieldGroup`` instance which the ``ContentPane`` is owned.

    """
    refer = models.CharField(max_length=120, blank=False, db_index=True, verbose_name=_("Class name"))
    name = models.CharField(max_length=120, blank=False, db_index=True,unique=True, verbose_name=_("Field name"))
    verbose_name = models.CharField(max_length=120, blank=False, verbose_name=_("Verbose name"))
    typo = models.CharField(max_length=20, blank=False, db_index=True, verbose_name=_("Field type"), choices=single_list_to_tuple(FIELD_TYPES))
    max_length = models.IntegerField(null=True, blank=True, verbose_name=_("Length"))
    order = models.IntegerField(null=True, blank=True, default=None, verbose_name=_("Order"))
    blank = models.BooleanField(default=True, verbose_name=_("Blank"))
    choices = models.TextField(null=True, blank=True, verbose_name=_("Choices"))
    default_value = models.CharField(max_length=80, null=True, blank=True, verbose_name=_("Default value"))
    help_text = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Help Text'))
    html_attrs = hstore.DictionaryField(db_index=True, null=True, blank=True, default=None, verbose_name=_("html Attributes"))

    # relations
    group = models.ForeignKey(DynamicFieldGroup, null=True, blank=True, related_name="dynamic_fields", verbose_name=_("Groups"))
    content_pane = models.ForeignKey(ContentPane, null=True, blank=True, related_name="dynamic_fields", verbose_name=_("Panel"))

    class Meta:
        verbose_name = _('Dynamic Field')
        verbose_name_plural = _('Dynamic Fields')
        # ordering = ['pk']

    def __unicode__(self):
        return self.verbose_name or self.name

    @property
    def has_blank_option(self):
        return self.blank and self.typo not in FIELD_TYPES_WITHOUT_BLANK_OPTION