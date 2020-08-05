from django.shortcuts import render

from csss.views_helper import create_frosh_context


def index(request):
    return render(request, 'events/frosh/2017/index.html', create_frosh_context())


def conditions(request):
    return render(request, 'events/frosh/2017/conditions.html', create_frosh_context())


def frosh(request):
    return render(request, 'events/frosh/2017/frosh.html', create_frosh_context())
