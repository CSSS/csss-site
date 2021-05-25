from django.shortcuts import render

from csss.views_helper import create_main_context

TAB = 'events'


def regular_events(request):
    return render(request, 'events/regular_events.html', create_main_context(request, TAB))


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


def mountain_madness2021(request):
    return render(request, 'events/mountain_madness2021.html', create_main_context(request, TAB))


def fall_hacks2020(request):
    return render(request, 'events/fall_hacks2020.html', create_main_context(request, TAB))


def fall_hacks_submissions2020(request):
    return render(request, 'events/fall_hacks_submissions2020.html', create_main_context(request, TAB))
