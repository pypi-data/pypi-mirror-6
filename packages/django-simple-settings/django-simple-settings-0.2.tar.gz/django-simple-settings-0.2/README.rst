======================
Django Simple Settings
======================

A very simple settings configurable in Django Admin Panel. Supported types: bool, float, int, str.

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

    $ python manage.py migrate


Usage
-----

Get settings:

.. code-block:: python

    from simple_settings import settings

    print settings.get('is_feature_available')
    print settings.get['is_feature_available']

Get all settings as dict:

.. code-block:: python

    all_settings = dict(settings)

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
