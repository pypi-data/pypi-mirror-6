# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from models import Group
from factories import GroupFactory
import simplejson as json

GROUP_ID = 47241470410797
GROUP_NAME = u'Кока-Кола'

class OdnoklassnikiGroupsTest(TestCase):

    def test_refresh_group(self):

        instance = Group.remote.fetch(ids=[GROUP_ID])[0]
        self.assertEqual(instance.name, GROUP_NAME)

        instance.name = 'temp'
        instance.save()
        self.assertEqual(instance.name, 'temp')

        instance.refresh()
        self.assertEqual(instance.name, GROUP_NAME)

    def test_fetch_groups(self):

        self.assertEqual(Group.objects.count(), 0)
        instance = Group.remote.fetch(ids=[GROUP_ID])[0]

        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(instance.id, GROUP_ID)
        self.assertEqual(instance.name, GROUP_NAME)

    def test_parse_group(self):

        response = u'''[{
                    "uid": "53923499278353",
                    "name": "Группа для тестирования нового сервиса",
                    "description": "Группа для тестирования нового сервиса",
                    "shortname": "newservicetesting",
                    "picAvatar": "http://groupava2.odnoklassniki.ru/getImage?photoId=476991575825&photoType=4",
                    "shop_visible_admin": false,
                    "shop_visible_public": false,
                    "members_count": 12463
                }]'''
        instance = Group()
        instance.parse(json.loads(response)[0])
        instance.save()

        self.assertEqual(instance.id, 53923499278353)
        self.assertEqual(instance.name, u'Группа для тестирования нового сервиса')
        self.assertEqual(instance.description, u'Группа для тестирования нового сервиса')
        self.assertEqual(instance.shortname, 'newservicetesting')
        self.assertEqual(instance.picavatar, 'http://groupava2.odnoklassniki.ru/getImage?photoId=476991575825&photoType=4')
        self.assertEqual(instance.shop_visible_admin, False)
        self.assertEqual(instance.shop_visible_public, False)
        self.assertEqual(instance.members_count, 12463)