from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

TAB = 'events'


def fall_hacks2020(request):
    return render(request, 'fall_hacks/2020/fall_hacks2020.html', create_main_context(request, TAB))


def fall_hacks_submissions2020(request):
    return render(
        request, 'fall_hacks/2020/fall_hacks_submissions2020.html', create_main_context(request, TAB)
    )
