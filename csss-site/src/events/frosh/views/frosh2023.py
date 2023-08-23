from random import randrange

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

from events.frosh.views.create_frosh_context import create_frosh_context


def index(request):
    return render(request, 'frosh/2023/index.html', create_frosh_context())


def frosh(request):
    return render(request, 'frosh/2023/frosh.html', create_frosh_context())


def secret(request):
    if randrange(0, 10) < 7:
        raise Http404('Not sure if there is a secret here. Please refresh your page and try again.')
    return HttpResponseRedirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


def sponsor(request):
    return render(request, 'frosh/2023/sponsor/index.html', create_frosh_context())
