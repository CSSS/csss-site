from django.shortcuts import render

from csss.views_helper import create_context

TAB = 'events'

FROSH_TAB = 'frosh_2013_tab'


def index(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2013/index.html', context)


def schedule(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'schedule'
    return render(request, 'events/frosh/2013/schedule.html', context)


def registration(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'registration'
    return render(request, 'events/frosh/2013/registration.html', context)


def faq(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'faq'
    return render(request, 'events/frosh/2013/faq.html', context)


def sponsors(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'faq'
    return render(request, 'events/frosh/2013/sponsors.html', context)


def contact(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'contact'
    return render(request, 'events/frosh/2013/contact.html', context)