Django Vkontakte Wall Statistic
===============================

[![PyPI version](https://badge.fury.io/py/django-vkontakte-wall-statistic.png)](http://badge.fury.io/py/django-vkontakte-wall-statistic) [![Build Status](https://travis-ci.org/ramusus/django-vkontakte-wall-statistic.png?branch=master)](https://travis-ci.org/ramusus/django-vkontakte-wall-statistic) [![Coverage Status](https://coveralls.io/repos/ramusus/django-vkontakte-wall-statistic/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-vkontakte-wall-statistic)

Приложение позволяет взаимодействовать со статистикой сообщений Вконтакте через Вконтакте API и парсер используя стандартные модели Django

Установка
---------

    pip install django-vkontakte-wall-statistic

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'vkontakte_api',
        'vkontakte_users',
        'vkontakte_groups',
        'vkontakte_wall',
        'vkontakte_wall_statistic',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                         # to keep in DB expired access tokens
    OAUTH_TOKENS_VKONTAKTE_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_VKONTAKTE_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_VKONTAKTE_SCOPE = ['ads,wall,photos,friends,stats']    # application scopes
    OAUTH_TOKENS_VKONTAKTE_USERNAME = ''                                # user login
    OAUTH_TOKENS_VKONTAKTE_PASSWORD = ''                                # user password
    OAUTH_TOKENS_VKONTAKTE_PHONE_END = ''                               # last 4 digits of user mobile phone

Покрытие методов API
--------------------

* [stats.get](http://vk.com/dev/stats.getPostStats) – возвращает статистику рекламной записи сообщества;

Примеры использования
---------------------

### Получение статистики группы

Получение статистики группы через API

    >>> from vkontakte_groups.models import Group
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> group.fetch_statistic(source='api')

Статистика, полученная через API доступна через менеджер

    >>> stat = group.statistics_api.all()[0]
    >>> stat.__dict__
    {'_state': <django.db.models.base.ModelState at 0xa2812ac>,
     'age_18': 240,
     'age_18_21': 86,
     'age_21_24': 75,
     'age_24_27': 59,
     'age_27_30': 31,
     'age_30_35': 23,
     'age_35_45': 9,
     'age_45': 13,
     'date': datetime.date(2012, 3, 14),
     'females': 295,
     'fetched': datetime.datetime(2012, 9, 12, 0, 50, 42, 597930),
     'group_id': 14,
     'id': 182,
     'males': 406,
     'views': 1401,
     'visitors': 702}