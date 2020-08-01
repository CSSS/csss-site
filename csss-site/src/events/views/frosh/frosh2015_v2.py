from django.shortcuts import render

from csss.views_helper import create_context


def index(request):
    return render(request, 'events/frosh/2015_v2/index.html', create_context())


def conditions(request):
    return render(request, 'events/frosh/2015_v2/conditions.html', create_context())


def contact(request):
    return render(request, 'events/frosh/2015_v2/contactus.html', create_context())


def team(request):
    return render(request, 'events/frosh/2015_v2/team.html', create_context())


def frosh(request):
    return render(request, 'events/frosh/2015_v2/frosh.html', create_context())