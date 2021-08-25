from django.shortcuts import render

from events.frosh.views.create_frosh_context import create_frosh_context


def index(request):
    return render(request, 'frosh/2016/index.html', create_frosh_context())


def conditions(request):
    return render(request, 'frosh/2016/conditions.html', create_frosh_context())


def frosh(request):
    return render(request, 'frosh/2016/frosh.html', create_frosh_context())
