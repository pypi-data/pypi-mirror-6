# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _
from django.core.exceptions import MultipleObjectsReturned, ImproperlyConfigured
from django.conf import settings
from odnoklassniki_api import fields
from odnoklassniki_api.models import OdnoklassnikiManager, OdnoklassnikiModel, OdnoklassnikiPKModel, OdnoklassnikiDeniedAccessError, OdnoklassnikiContentError
from datetime import datetime
from urllib import unquote
import logging
import re
import simplejson as json

log = logging.getLogger('odnoklassniki_group')


class GroupRemoteManager(OdnoklassnikiManager):

    fields = [
        'uid',
        'name',
        'description',
        'shortname',
        'pic_avatar',
        'photo_id',
        'shop_visible_admin',
        'shop_visible_public',
        'members_count',
        'premium',
        'private',
#        'admin_id'
    ]

    def fetch(self, *args, **kwargs):
        if 'ids' in kwargs:
            kwargs['uids'] = ','.join(map(lambda i: str(i), kwargs.pop('ids')))
        if 'fields' not in kwargs:
            kwargs['fields'] = ','.join(self.fields)
        return super(GroupRemoteManager, self).fetch(*args, **kwargs)


class Group(OdnoklassnikiPKModel):
    class Meta:
        verbose_name = _('Odnoklassniki group')
        verbose_name_plural = _('Odnoklassniki groups')

#     resolve_screen_name_type = 'group'
    methods_namespace = 'group'
    remote_pk_field = 'uid'
    slug_prefix = 'group'

    name = models.CharField(max_length=800)
    description = models.TextField()
    shortname = models.CharField(max_length=50)

    members_count = models.PositiveIntegerField()

    photo_id = models.PositiveIntegerField(null=True)
    picavatar = models.URLField()

    premium = models.NullBooleanField()
    private = models.NullBooleanField()
    shop_visible_admin = models.NullBooleanField()
    shop_visible_public = models.NullBooleanField()

    remote = GroupRemoteManager(methods={
        'get': 'getInfo',
#        'search': 'search',
    })

    def __unicode__(self):
        return self.name

    def remote_link(self):
        return 'http://vk.com/club%d' % self.remote_id

    @property
    def refresh_kwargs(self):
        return {'ids': [self.pk]}