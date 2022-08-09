from django.shortcuts import render, redirect
from random import randrange
from django.http import Http404

from events.frosh.views.create_frosh_context import create_frosh_context


def index(request):
    return render(request, 'frosh/2022/index.html', create_frosh_context())


def frosh(request):
    return render(request, 'frosh/2022/frosh.html', create_frosh_context())


def secret(request):
    test = randrange(0, 10)
    if test < 7:
        raise Http404('Not sure if there is a secret here. Please refresh your page and try again.')
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ', permanent=True)
