from django.shortcuts import render

from csss.views.context_creation.create_main_context import create_main_context

TAB = 'events'


def frosh_week(request):
    return render(request, 'frosh/frosh_week.html', create_main_context(request, TAB))
