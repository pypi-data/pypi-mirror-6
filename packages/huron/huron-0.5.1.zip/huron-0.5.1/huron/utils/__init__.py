"""

.. module:: utils
   :platform: Unix
   :synopsis: Utilities for Huron

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

Here you can find some tools for your Django Huron-based applications.


How to use it
=============

If you want to use static files, like CKEditor or Colorbox, add
*huron.simple_news* on your INSTALLED_APPS.


ColorBox
========

huron.utils have ColorBox, which is used by some Huron's apps,
like :py:mod:`huron.simple_medias_manager`

.. note::

    The jquery.colorbox.js  and jquery.colorbox-min.js used in admin are
    tweaked to use *jQuery* as *django.jQuery*. So you can't use it on your
    front.


CKEditor
========

.. note::

    The jQuery adapter *adapters/django.jquery.js* is tweaked to use *jQuery*
    as *django.jQuery*. So you can't use it on your front. You have to use the
    original adapter *adapters/jquery.js*

"""
