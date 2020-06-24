from django.shortcuts import render

from administration.views.views_helper import create_context

TAB_STRING = 'events'


def index(request):
    return render(request, 'events/calendar.html', create_context(request, TAB_STRING))


def gm(request):
    return render(request, 'events/gm.html', create_context(request, TAB_STRING))


def board_games(request):
    return render(request, 'events/board_games.html', create_context(request, TAB_STRING))


def frosh_week(request):
    return render(request, 'events/frosh_week.html', create_context(request, TAB_STRING))


def mountain_madness2020(request):
    return render(request, 'events/mountain_madness2020.html', create_context(request, TAB_STRING))

# Create your views here.
