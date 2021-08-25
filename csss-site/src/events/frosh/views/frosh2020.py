from django.shortcuts import render

from events.frosh.views.create_frosh_context import create_frosh_context


def index(request):
    return render(request, 'frosh/2020/index.html', create_frosh_context())


def frosh(request):
    return render(request, 'frosh/2020/frosh.html', create_frosh_context())
