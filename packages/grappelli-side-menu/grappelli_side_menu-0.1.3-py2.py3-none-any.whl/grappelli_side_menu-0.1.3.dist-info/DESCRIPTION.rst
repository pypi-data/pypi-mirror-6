=============================
grappelli-side-menu
=============================

.. image:: https://badge.fury.io/py/grappelli-side-menu.png
    :target: https://badge.fury.io/py/grappelli-side-menu


Side menu for Grappelli, the Django admin Interface

.. image:: ./grappelli-side-menu.jpg

Quickstart
----------

Install grappelli-side-menu::

    pip install grappelli-side-menu

Add "grappelli_menu" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        'grappelli_menu',
        'grappelli',
        'django.contrib.admin',
        .....
    )

Add `django.core.context_processors.request` to your TEMPLATE_CONTEXT_PROCESSORS if it's not there already::

    TEMPLATE_CONTEXT_PROCESSORS = (
        .....
        "django.core.context_processors.request",
    )

Features
--------

* TODO



History
-------


0.1.3 (2014-28-04)
++++++++++++++++++

* Fix: Hiding the menu in the login and logout screen


0.1.1,0.1.2 (2014-25-04)
++++++++++++++++++++++++

* Fix: Including the css file


0.1.0 (2014-25-04)
++++++++++++++++++

* First release on PyPI.

