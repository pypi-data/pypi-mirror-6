"""

.. module:: simple_news
   :platform: Unix
   :synopsis: Really simple news application for Django

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

This application provides :

* Listing of news
* Singles of news
* RSS Feed
* Sitemap
* Administration
* Simple templates

How to install
==============

Firstly, add *huron.simple_news* on your INSTALLED_APPS.

Then, add this line on your URL patterns :
::

    url(r'^news/', include("huron.simple_news.urls", namespace="simple_news")),

Of course, you can change your root pattern. Namespace should be simple_news

Run *syncdb*.

Helpers
=======

"""

from huron.simple_news.models import News

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from datetime import datetime


def get_latest_news():
    """

    Load a queryset with the last published news.

    :returns: news
    :rtype: queryset object

    .. note::
        The object returned is a queryset. You can use QuerySet methods from
        Django. Read the `documentation
        <https://docs.djangoproject.com/en/1.5/ref/models/querysets/>`_

    """
    return News.objects.filter(Q(date_unpub__gte=datetime.today()) | Q(date_unpub=None),
                               date_pub__lte=datetime.today(),
                               published=True)


def get_latest_news_by_category(category_slug):
    """

    Load a news queryset for the category slug given in parameters.

    :param slug: Slug of the category asked
    :type slug: str
    :returns: news
    :rtype: queryset object

    .. note::
        The object returned is a queryset. You can use QuerySet methods from
        Django. Read the `documentation
        <https://docs.djangoproject.com/en/1.5/ref/models/querysets/>`_

    """
    return News.objects.filter(Q(date_unpub__gte=datetime.today()) | Q(date_unpub=None),
                               date_pub__lte=datetime.today(),
                               categories__slug=category_slug,
                               published=True)


def get_new_by_slug(slug):
    """

    Load a news queryset for the slug given in parameters.

    :param slug: Slug of the new asked
    :type slug: str
    :returns: news
    :rtype: queryset object

    .. note::
        The object returned is a queryset. You can use QuerySet methods from
        Django. Read the `documentation
        <https://docs.djangoproject.com/en/1.5/ref/models/querysets/>`_

    """
    try:
        new = News.objects.get(Q(date_unpub__gte=datetime.today()) | Q(date_unpub=None),
                               slug=slug, date_pub__lte=datetime.today(),
                               published=True)
    except ObjectDoesNotExist:
        raise Http404
    return new
