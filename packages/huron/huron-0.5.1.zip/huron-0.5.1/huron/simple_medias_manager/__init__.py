"""

.. module:: simple_medias_manager
   :platform: Unix
   :synopsis: Really simple media manager for Django

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

This application could be used with :py:mod:`huron.utils` and the ColorBox
static files.

How to install
==============

Firstly, add *huron.simple_medias_manager* on your INSTALLED_APPS.

Then, add this lines on your urls.py, after your own url pattern :
::

    import huron.simple_medias_manager as simple_medias_manager
    urlpatterns += simple_medias_manager.get_url()

Run *syncdb*.

"""

from huron.simple_medias_manager.urls import mediapatterns


def get_url():
    return mediapatterns
