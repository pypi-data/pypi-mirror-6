# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes import generic
from odnoklassniki_api.models import OdnoklassnikiManager, OdnoklassnikiPKModel
from odnoklassniki_api.decorators import fetch_all, atomic
from odnoklassniki_api.fields import JSONField
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

    # this fields available from entities of discussions
    pic128x128 = models.URLField()
    pic50x50 = models.URLField()
    pic640x480 = models.URLField()

    premium = models.NullBooleanField()
    private = models.NullBooleanField()
    shop_visible_admin = models.NullBooleanField()
    shop_visible_public = models.NullBooleanField()

    attrs = JSONField(null=True)

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
        # in entity of discussion
        if 'main_photo' in response:
            if 'id' in response['main_photo']:
                del response['main_photo']['id']
            response.update(response.pop('main_photo'))

        # pop avatar, because self.pic50x50 the same
        response.pop('picAvatar', None)

        super(Group, self).parse(response)

    @atomic
    def update_users(self, **kwargs):
        if 'odnoklassniki_users' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("Application 'odnoklassniki_users' not in INSTALLED_APPS")

        ids = Group.remote.get_members_ids(group=self)
        self.users = User.remote.fetch(ids=ids)

        return self.users.all()

'''
Fields, dependent on other applications
'''
def get_improperly_configured_field(app_name, decorate_property=False):
    def field(self):
        raise ImproperlyConfigured("Application '%s' not in INSTALLED_APPS" % app_name)
    if decorate_property:
        field = property(field)
    return field

if 'odnoklassniki_users' in settings.INSTALLED_APPS:
    from odnoklassniki_users.models import User
    from m2m_history.fields import ManyToManyHistoryField
    users = ManyToManyHistoryField(User)
else:
    users = get_improperly_configured_field('odnoklassniki_users', True)

if 'odnoklassniki_discussions' in settings.INSTALLED_APPS:
    from odnoklassniki_discussions.models import Discussion
    discussions = generic.GenericRelation(Discussion, content_type_field='owner_content_type', object_id_field='owner_id')
    discussions_count = models.PositiveIntegerField(null=True)
    def fetch_discussions(self, **kwargs):
        return Discussion.remote.fetch(group=self, **kwargs)
else:
    discussions = get_improperly_configured_field('odnoklassniki_discussions', True)
    discussions_count = discussions
    fetch_discussions = discussions

Group.add_to_class('users', users)
Group.add_to_class('discussions', discussions)
Group.add_to_class('discussions_count', discussions_count)
Group.add_to_class('fetch_discussions', fetch_discussions)