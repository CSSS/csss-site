from django.shortcuts import render

from csss.views_helper import create_context

TAB = 'events'

FROSH_TAB = 'frosh_2015_tab'


def index(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2015/index.html', context)


def schedule(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2015/schedule.html', context)



def registration(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2015/registration.html', context)


def faq(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2015/faq.html', context)


def contact_us(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2015/contact.html', context)


def sponsors(request):
    context = create_context(request, TAB)
    context[FROSH_TAB] = 'index'
    return render(request, 'events/frosh/2015/sponsors.html', context)
