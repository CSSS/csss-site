# from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect


import logging
logger = logging.getLogger('csss_site')


def login(request):
    logger.info(f"[administration/views.py login()] request.POST={request.POST}")
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        logger.info(f"[administration/views.py login()] username = {username}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            dj_login(request, user)
            logger.info("[administration/views.py login()] it was a successful login")
    logger.info("[administration/views.py login()] it was an insuccessful login")
    return HttpResponseRedirect('/')


def logout(request):
    dj_logout(request)
    return HttpResponseRedirect('/')
