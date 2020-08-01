from django.shortcuts import render

from csss.views_helper import create_context


def index(request):
    return render(request, 'events/frosh/2015/index.html', create_context())


def schedule(request):
    return render(request, 'events/frosh/2015/schedule.html', create_context())



def registration(request):
    return render(request, 'events/frosh/2015/registration.html', create_context())


def faq(request):
    return render(request, 'events/frosh/2015/faq.html', create_context())


def contact_us(request):
    return render(request, 'events/frosh/2015/contact.html', create_context())


def sponsors(request):
    return render(request, 'events/frosh/2015/sponsors.html', create_context())
