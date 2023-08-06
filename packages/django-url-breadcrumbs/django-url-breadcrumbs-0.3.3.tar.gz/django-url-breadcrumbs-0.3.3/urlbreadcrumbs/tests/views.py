#encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext


def simple_view(request, template):
    return render_to_response(template, {}, context_instance=RequestContext(request))
