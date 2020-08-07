from django.shortcuts import render

from csss.views_helper import create_main_context

TAB = 'events'


def index(request):
    return render(request, 'events/calendar.html', create_main_context(request, TAB))


def gm(request):
    return render(request, 'events/gm.html', create_main_context(request, TAB))


def board_games(request):
    return render(request, 'events/board_games.html', create_main_context(request, TAB))


def frosh_week(request):
    return render(request, 'events/frosh/frosh_week.html', create_main_context(request, TAB))


def frosh_2013(request):
    return render(request, 'events/frosh/2013/index.html', create_main_context(request, TAB))


def frosh_2014(request):
    return render(request, 'events/frosh/2014/index.html', create_main_context(request, TAB))


def frosh_2015(request):
    return render(request, 'events/frosh/2015/index.html', create_main_context(request, TAB))


def mountain_madness2020(request):
    return render(request, 'events/mountain_madness2020.html', create_main_context(request, TAB))
