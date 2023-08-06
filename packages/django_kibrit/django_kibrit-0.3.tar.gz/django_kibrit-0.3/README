django_kibrit
=============

A git version parser for django templates.

Usage:
------

The intent of django_kibrit is to burn the css cache of the client upon a change in the project.

    # Somewhere in your templates
    <link href="{{ STATIC_URL }}css/screen.css{{ KIBRIT_REVISION }}" media="screen, projection" rel="stylesheet" type="text/css" />

Installation:
------------

    pip install django_kibrit

Kibrit makes use of the `memcached` library in django. To enable this place

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        },
    }

To use kibrit on your templates append the following 2 lines at the end of your projects `settings.py`.

    TEMPLATE_CONTEXT_PROCESSORS += ('django_kibrit.context_processors.revision',)
    INSTALLED_APPS += 'django_kibrit',

The package can try to detect .git in your project automatically but it is best if you explicitly set KIBRIT_PATH in your settings to where the .git file is in your project.

    KIBRIT_PATH = '/path/to/your/.git' # You've found it when 'ls -al | grep .git' prints the .git file
