from django.shortcuts import render

from csss.views_helper import create_frosh_context


def index(request):
    return render(request, 'events/frosh/2014/index.html', create_frosh_context())


def schedule(request):
    return render(request, 'events/frosh/2014/schedule.html', create_frosh_context())


def registration(request):
    return render(request, 'events/frosh/2014/registration.html', create_frosh_context())


def faq(request):
    return render(request, 'events/frosh/2014/faq.html', create_frosh_context())


def sponsors(request):
    return render(request, 'events/frosh/2014/sponsors.html', create_frosh_context())


def contact(request):
    return render(request, 'events/frosh/2014/contact.html', create_frosh_context())
