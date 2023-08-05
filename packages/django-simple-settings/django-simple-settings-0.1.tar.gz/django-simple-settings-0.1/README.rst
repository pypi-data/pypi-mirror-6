======================
Django Simple Settings
======================

A very simple settings configurable in Django Admin Panel.

Intsallation
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

2. Add context processor if you would like:

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        '...',
        'simple_settings.context_processors.simple_settings',
    )

3. Create models:

.. code-block:: bash

    $ python manage.py migrate


Usage
-----

Settings can be set in Django Admin.

Get settings:

.. code-block:: python

    from simple_settings import settings

    print settings.get('is_feature_available')
    print settings.get['is_feature_available']
    
Get settings in template:

.. code-block:: html+django

    {{ simple_settings.is_feature_available }}
