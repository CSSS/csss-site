from django.shortcuts import render

from csss.views_helper import create_frosh_context

FROSH_TAB = 'frosh_2011_tab'


def index(request):
    context = create_frosh_context()
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2012/index.html', context)


def schedule(request):
    context = create_frosh_context()
    context[FROSH_TAB] = 'schedule'
    return render(request, 'events/frosh/2012/schedule.html', context)


def registration(request):
    context = create_frosh_context()
    context[FROSH_TAB] = 'registration'
    return render(request, 'events/frosh/2012/registration.html', context)


def faq(request):
    context = create_frosh_context()
    context[FROSH_TAB] = 'faq'
    return render(request, 'events/frosh/2012/faq.html', context)


def contact(request):
    context = create_frosh_context()
    context[FROSH_TAB] = 'contact'
    return render(request, 'events/frosh/2012/contact.html', context)


def sponsors(request):
    context = create_frosh_context()
    context[FROSH_TAB] = 'sponsors'
    return render(request, 'events/frosh/2012/sponsors.html', context)
