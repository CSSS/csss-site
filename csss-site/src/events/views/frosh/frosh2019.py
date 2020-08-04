from django.shortcuts import render

from csss.views_helper import create_context


def index(request):
    return render(request, 'events/frosh/2019/index.html', create_context())


def frosh(request):
    return render(request, 'events/frosh/2019/frosh.html', create_context())
