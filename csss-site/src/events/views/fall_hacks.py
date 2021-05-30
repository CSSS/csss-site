from django.shortcuts import render

from csss.views_helper import create_main_context

TAB = 'events'


def fall_hacks2020(request):
    return render(request, 'events/fall_hacks/2020/fall_hacks2020.html', create_main_context(request, TAB))


def fall_hacks_submissions2020(request):
    return render(
        request, 'events/fall_hacks/2020/fall_hacks_submissions2020.html', create_main_context(request, TAB)
    )
