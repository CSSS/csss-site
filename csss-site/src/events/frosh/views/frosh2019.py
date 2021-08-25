from django.shortcuts import render

from csss.views.context_creation.create_frosh_context import create_frosh_context


def index(request):
    return render(request, 'frosh/2019/index.html', create_frosh_context())


def frosh(request):
    return render(request, 'frosh/2019/frosh.html', create_frosh_context())
