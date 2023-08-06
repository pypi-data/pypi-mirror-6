from datetime import datetime

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from huron.pages.models import Page

"""

.. module:: pages
   :platform: Unix
   :synopsis: Pages application for Django

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


def get_page_by_slug(slug):
    """

    Load a page queryset for the slug given in paramters.
    Some paramters are given by default like :

    * State has to be ``published``
    * Published date has to be passed from ``now``
    * Unpublished date has to be greater than ``now`` or ``None``

    :param slug: Slug of the page asked
    :type slug: str
    :returns: page
    :rtype: queryset object

    .. note::
        The object returned is a queryset. You can use QuerySet methods from
        Django. Read the `documentation
        <https://docs.djangoproject.com/en/1.5/ref/models/querysets/>`_

    """
    try:
        page = Page.objects.get(Q(date_unpub__gte=datetime.today()) | Q(date_unpub=None),
                                slug=slug, date_pub__lte=datetime.today(),
                                status='published')
    except ObjectDoesNotExist:
        raise Http404
    return page
