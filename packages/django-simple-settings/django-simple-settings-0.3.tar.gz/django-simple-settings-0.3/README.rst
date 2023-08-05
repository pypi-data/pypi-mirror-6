======================
Django Simple Settings
======================

A very simple settings configurable in Django Admin Panel. Supported types: bool, float, int, str.

.. image:: https://badge.fury.io/py/django-simple-settings.png
   :target: http://badge.fury.io/py/django-simple-settings

.. image:: https://api.travis-ci.org/alikus/django-simple-settings.png
   :target: https://travis-ci.org/alikus/django-simple-settings

.. image:: https://coveralls.io/repos/alikus/django-simple-settings/badge.png?branch=master
    :target: https://coveralls.io/r/alikus/django-simple-settings?branch=master

Installation
------------

1. Install a package.

.. code-block:: bash

    $ pip install django-simple-settings

2. Add "simple_settings" to your INSTALLED_APPS setting:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'simple_settings',
    )

3. Add context processor if you would like:

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        '...',
        'simple_settings.context_processors.simple_settings',
    )

4. Create models:

.. code-block:: bash

    $ python manage.py migrate || python manage.py syncdb

Usage
-----

Get settings:

.. code-block:: python

    from simple_settings import settings

    print settings.get('is_feature_available')
    print settings.get('is_feature_available', default=False)
    print settings['is_feature_available']

Get all settings as dict:

.. code-block:: python

    print settings.all()

Get settings in template if you include context processor:

.. code-block:: html+django

    {{ simple_settings.is_feature_available }}

Set settings:

.. code-block:: python

    settings.set('is_feature_available', True)
    settings.set('pi', 3.14159265359)
    settings.set('answer', 42)
    settings.set('metallica', 'Yeah!')

Delete settings:

.. code-block:: python

    settings.delete('is_feature_available')

Settings
--------
Default application settings can be overriden in settings.py:

.. code-block:: python

    SIMPLE_SETTINGS_CACHE_TIMEOUT = 60 * 60 * 24 #  default cache timeout is one day
    SIMPLE_SETTINGS_CACHE_ALIAS = 'default' # default cache backend

Requirements
------------

* Python 2.6, 2.7, 3.3
* Django 1.3+
