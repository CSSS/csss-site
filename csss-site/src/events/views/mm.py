from django.shortcuts import render

from csss.views_helper import create_main_context

TAB = 'events'


def mountain_madness2020(request):
    return render(request, 'events/mm/2020/mountain_madness2020.html', create_main_context(request, TAB))


def mountain_madness2021(request):
    return render(request, 'events/mm/2021/mountain_madness2021.html', create_main_context(request, TAB))
