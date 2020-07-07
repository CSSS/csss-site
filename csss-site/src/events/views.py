from django.shortcuts import render

from csss.views_helper import create_context

TAB = 'events'
def index(request):
    return render(request, 'events/calendar.html', create_context(request, TAB))


def gm(request):
    return render(request, 'events/gm.html', create_context(request, TAB))


def board_games(request):
    return render(request, 'events/board_games.html', create_context(request, TAB))


def frosh_week(request):
    return render(request, 'events/frosh_week.html', create_context(request, TAB))


def mountain_madness2020(request):
    return render(request, 'events/mountain_madness2020.html', create_context(request, TAB))

# Create your views here.
