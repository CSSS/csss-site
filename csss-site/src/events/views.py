from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

TAB = 'events'


def regular_events(request):
    return render(request, 'events/regular_events.html', create_main_context(request, TAB))
