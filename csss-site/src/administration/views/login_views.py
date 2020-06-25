from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from django.conf import settings

import logging
logger = logging.getLogger('csss_site')


def login(request):
    logger.info(f"[administration/login_views.py login()] request.POST={request.POST}")
    if 'username' in request.POST and 'password' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        logger.info(f"[administration/login_views.py login()] username = {username}")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            dj_login(request, user)
            logger.info("[administration/views.py login()] it was a successful login")
<<<<<<< HEAD:csss-site/src/administration/views/login_views.py
    logger.info("[administration/views.py login()] it was an unsuccessful login")
=======
    logger.info("[administration/views.py login()] it was an insuccessful login")
>>>>>>> f2648f8f41c3c733115db055a8b9bed7438d1056:csss-site/src/administration/views.py
    return HttpResponseRedirect(settings.URL_ROOT)


def logout(request):
    dj_logout(request)
    return HttpResponseRedirect(settings.URL_ROOT)


def db_dump(request):
    dict['about'] = {}
    return HttpResponseRedirect(settings.URL_ROOT)
