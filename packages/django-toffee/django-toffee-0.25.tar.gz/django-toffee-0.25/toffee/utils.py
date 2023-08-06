from django.shortcuts import render_to_response
from django.template import RequestContext


def toffee_render_to_response(request, content, navbar=None, sidebar=None, footer=None, logo='', title="Page Title"):
    return render_to_response('app_template.html', locals(), context_instance=RequestContext(request))