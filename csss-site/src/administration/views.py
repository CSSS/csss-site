from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from django.conf import settings

from about.models import Term, Officer, AnnouncementEmailAddress
from announcements.models import Post
from documents.models import Repo, Event, Album, Picture, Video, Media, SubCategory
from elections.models import NominationPage, Nominee

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
    return HttpResponseRedirect(settings.URL_ROOT)


def logout(request):
    dj_logout(request)
    return HttpResponseRedirect(settings.URL_ROOT)

def db_dump(request):
    dict['about'] = {}

    return HttpResponseRedirect(settings.URL_ROOT)
