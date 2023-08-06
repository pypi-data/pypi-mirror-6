from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from huron.pages.models import Page

"""

.. module:: huron.pages.views
   :platform: Unix
   :synopsis: Pages application for Django - views module

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

"""


def page(request, page_slug):
    """

    Render a page with the page template ``page.html`` from the website with
    the page context of the page asked.

    :param slug: Slug of the page asked
    :type slug: str
    :returns: page
    :rtype: Page object

    .. note::
        To know more about context informations send, please check the
        model :py:class:`huron.pages.models.Page`

    """
    variables = {}
    select_page = get_object_or_404(Page, slug=page_slug)

    variables['page'] = select_page
    request_context = RequestContext(request, variables)

    return render_to_response('page.html', context_instance=request_context)
