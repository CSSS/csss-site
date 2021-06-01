from django.shortcuts import render

from csss.views_helper import create_main_context

TAB = 'events'


def frosh_week(request):
    return render(request, 'frosh/frosh_week.html', create_main_context(request, TAB))
