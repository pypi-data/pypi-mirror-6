from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from huron.references.models import Reference
from utils.view_utils import get_variables


def references(request, page_slug):
    variables = get_variables()
    references = Reference.objects.all()

    request_context = RequestContext(request, variables)

    return render_to_response('references.html', context_instance=request_context)
