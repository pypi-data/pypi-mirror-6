# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes import generic
from odnoklassniki_api.models import OdnoklassnikiManager, OdnoklassnikiPKModel
from odnoklassniki_api.decorators import fetch_all, atomic
import logging

log = logging.getLogger('odnoklassniki_groups')


class GroupRemoteManager(OdnoklassnikiManager):

    @atomic
    def fetch(self, ids, **kwargs):
        kwargs['uids'] = ','.join(map(lambda i: str(i), ids))
        kwargs['fields'] = self.get_request_fields('group')
        return super(GroupRemoteManager, self).fetch(**kwargs)

    def update_members_count(self, instances, group, *args, **kwargs):
        group.members_count = len(instances)
        group.save()
        return instances

    @atomic
    @fetch_all(return_all=update_members_count, always_all=True)
    def get_members_ids(self, group, count=1000, **kwargs):
        kwargs['uid'] = group.pk
        kwargs['count'] = count
        response = self.api_call('get_members', **kwargs)
        ids = [m['userId'] for m in response['members']]
        return ids, response


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

    members_count = models.PositiveIntegerField(null=True)

    photo_id = models.BigIntegerField(null=True)
    pic_avatar = models.URLField()

    premium = models.NullBooleanField()
    private = models.NullBooleanField()
    shop_visible_admin = models.NullBooleanField()
    shop_visible_public = models.NullBooleanField()

    remote = GroupRemoteManager(methods={
        'get': 'getInfo',
        'get_members': 'getMembers',
    })

    def __unicode__(self):
        return self.name

    @property
    def refresh_kwargs(self):
        return {'ids': [self.pk]}

    def parse(self, response):
        # avatar
        if 'picAvatar' in response:
            response['pic_avatar'] = response.pop('picAvatar')
        super(Group, self).parse(response)

    @atomic
    def update_users(self, **kwargs):
        if 'odnoklassniki_users' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("Application 'odnoklassniki_users' not in INSTALLED_APPS")

        ids = Group.remote.get_members_ids(group=self)
        self.users = User.remote.fetch(ids=ids)

        return self.users

'''
Fields, dependent on other applications
'''

if 'odnoklassniki_users' in settings.INSTALLED_APPS:
    from odnoklassniki_users.models import User
    from m2m_history.fields import ManyToManyHistoryField
    users = ManyToManyHistoryField(User)
else:
    @property
    def users(self):
        raise ImproperlyConfigured("Application 'odnoklassniki_users' not in INSTALLED_APPS")

if 'odnoklassniki_discussions' in settings.INSTALLED_APPS:
    from odnoklassniki_discussions.models import Discussion
    discussions = generic.GenericRelation(Discussion, content_type_field='owner_content_type', object_id_field='owner_id')
    discussions_count = models.PositiveIntegerField(null=True)
else:
    @property
    def discussions(self):
        raise ImproperlyConfigured("Application 'odnoklassniki_discussions' not in INSTALLED_APPS")
    discussions_count = discussions

Group.add_to_class('users', users)
Group.add_to_class('discussions', discussions)
Group.add_to_class('discussions_count', discussions_count)