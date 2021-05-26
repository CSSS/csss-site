from django.shortcuts import render

from csss.views_helper import create_main_context

TAB = 'events'


def regular_events(request):
    return render(request, 'events/regular_events.html', create_main_context(request, TAB))


def frosh_week(request):
    return render(request, 'events/frosh/frosh_week.html', create_main_context(request, TAB))


def mountain_madness2020(request):
    return render(request, 'events/mountain_madness2020.html', create_main_context(request, TAB))


def mountain_madness2021(request):
    return render(request, 'events/mountain_madness2021.html', create_main_context(request, TAB))


def fall_hacks2020(request):
    return render(request, 'events/fall_hacks2020.html', create_main_context(request, TAB))


def fall_hacks_submissions2020(request):
    return render(request, 'events/fall_hacks_submissions2020.html', create_main_context(request, TAB))
