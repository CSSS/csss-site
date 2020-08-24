from django.shortcuts import render

from csss.views_helper import create_frosh_context


def index(request):
    return render(request, 'events/frosh/2020/index.html', create_frosh_context())


def frosh(request):
    return render(request, 'events/frosh/2020/frosh.html', create_frosh_context())
