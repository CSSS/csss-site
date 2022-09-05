from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

TAB = 'events'


def workshops(request):
    return render(request, 'workshops/main.html', create_main_context(request, TAB))
