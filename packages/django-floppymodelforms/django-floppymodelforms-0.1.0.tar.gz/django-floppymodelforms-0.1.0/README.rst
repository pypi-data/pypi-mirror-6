=======================
django-floppymodelforms
=======================

A hack to force Django's ModelForm to use floppyforms_ fields.

.. image:: https://badge.fury.io/py/django-floppymodelforms.png
    :target: http://badge.fury.io/py/django-floppymodelforms

.. image:: https://travis-ci.org/henriquebastos/django-floppymodelforms.png?branch=master
        :target: https://travis-ci.org/henriquebastos/django-floppymodelforms

.. image:: https://pypip.in/d/django-floppymodelforms/badge.png
        :target: https://crate.io/packages/django-floppymodelforms?version=latest

Installation
------------

Install the package:

.. code:: console

    pip install django-floppymodelforms


Usage
-----

Add ``floppymodelforms`` to your project's ``INSTALLED_APPS``
after the ``floppyforms`` app.

.. code:: python

    INSTALLED_APPS = (
        # ...
        'floppyforms',
        'floppymodelforms',
    )


Features
--------

* Add support for Django's extra form fields.


License
-------

BSD License


.. _floppyforms: https://github.com/brutasse/django-floppyforms
