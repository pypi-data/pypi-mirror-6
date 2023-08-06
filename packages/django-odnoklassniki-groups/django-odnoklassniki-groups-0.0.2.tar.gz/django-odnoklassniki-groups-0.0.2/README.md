Django Odnoklassniki Groups
=======================

[![PyPI version](https://badge.fury.io/py/django-odnoklassniki-groups.png)](http://badge.fury.io/py/django-odnoklassniki-groups) [![Build Status](https://travis-ci.org/ramusus/django-odnoklassniki-groups.png?branch=master)](https://travis-ci.org/ramusus/django-odnoklassniki-groups) [![Coverage Status](https://coveralls.io/repos/ramusus/django-odnoklassniki-groups/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-odnoklassniki-groups)

Приложение позволяет взаимодействовать с группами соц. сети Одноклассники, их статистикой и пользователями групп через OK API используя стандартные модели Django

Установка
---------

    pip install django-odnoklassniki-groups

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'odnoklassniki_api',
        'odnoklassniki_groups',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                             # to keep in DB expired access tokens
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_PUBLIC = ''                           # application public key
    OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_ODNOKLASSNIKI_SCOPE = ['']                                 # application scopes
    OAUTH_TOKENS_ODNOKLASSNIKI_USERNAME = ''                                # user login
    OAUTH_TOKENS_ODNOKLASSNIKI_PASSWORD = ''                                # user password

Покрытие методов API
--------------------

* [group.getInfo](http://apiok.ru/wiki/pages/viewpage.action?pageId=46137373#API%D0%94%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%86%D0%B8%D1%8F%28%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9%29-group.getInfo) – получение информации о группах;

Примеры использования
---------------------

### Получение группы

    >>> from odnoklassniki_groups.models import Group
    >>> Group.remote.fetch(ids=[16297716])
    [<Group: Coca-Cola>]