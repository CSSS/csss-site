from django.shortcuts import render

from events.frosh.views.create_frosh_context import create_frosh_context


def index(request):
    return render(request, 'frosh/2018/index.html', create_frosh_context())


def conditions(request):
    return render(request, 'frosh/2018/conditions.html', create_frosh_context())


def frosh(request):
    return render(request, 'frosh/2018/frosh.html', create_frosh_context())
