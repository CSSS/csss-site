import datetime
import json
import logging
import time

from django.conf import settings
from django.core import serializers
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Officer, Term
from administration.models import GDriveUser, GDrivePublicFile
from administration.models import NaughtyOfficer
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from .views_helper import there_are_multiple_entries, verify_access_logged_user_and_create_context

import xml.etree.ElementTree as ET

logger = logging.getLogger('csss_site')

GOOGLE_DRIVE_USERS_DB_RECORD_KEY = 'record_id'
GOOGLE_DRIVE_USERS_NAME_KEY = 'legal_name'
GOOGLE_DRIVE_USERS_GMAIL_KEY = 'gmail'
GOOGLE_DRIVE_USERS_FILE_ID_KEY = 'file_id'
GOOGLE_DRIVE_USERS_FILE_NAME_KEY = 'file_name'
GOOGLE_DRIVE_USERS_FILE_LINK_KEY = 'file_link'
TAB_STRING = 'administration'


def user_does_not_have_access_to_file(gmail, file_id):
    return len(GDriveUser.objects.filter(
        gmail=gmail,
        file_id=file_id
    )) == 0


def google_drive_file_is_publicly_available(file_id):
    return len(GDrivePublicFile.objects.filter(
        file_id=file_id
    )) > 0


def gdrive_index(request):
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    if 'error_message' in request.session:
        context['error_experienced'] = request.session['error_message'].split("<br>")
        del request.session['error_message']
    context['g_drive_users'] = GDriveUser.objects.all().filter().order_by('id')
    context['g_drive_public_links'] = GDrivePublicFile.objects.all().filter().order_by('id')
    context['GOOGLE_DRIVE_USERS_DB_RECORD_KEY'] = GOOGLE_DRIVE_USERS_DB_RECORD_KEY
    context['GOOGLE_DRIVE_USERS_NAME_KEY'] = GOOGLE_DRIVE_USERS_NAME_KEY
    context['GOOGLE_DRIVE_USERS_GMAIL_KEY'] = GOOGLE_DRIVE_USERS_GMAIL_KEY
    context['GOOGLE_DRIVE_USERS_FILE_ID_KEY'] = GOOGLE_DRIVE_USERS_FILE_ID_KEY
    context['GOOGLE_DRIVE_USERS_FILE_NAME_KEY'] = GOOGLE_DRIVE_USERS_FILE_NAME_KEY
    context['GOOGLE_DRIVE_USERS_FILE_LINK_KEY'] = GOOGLE_DRIVE_USERS_FILE_LINK_KEY
    return render(request, 'administration/resources/gdrive_management.html', context)


def add_users_to_gdrive(request):
    logger.info(f"[administration/gdrive_views.py add_users_to_gdrive()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        post_dict = parser.parse(request.POST.urlencode())
        if there_are_multiple_entries(post_dict, GOOGLE_DRIVE_USERS_NAME_KEY):
            number_of_entries = len(post_dict[GOOGLE_DRIVE_USERS_NAME_KEY])
            logger.info(
                f"[administration/gdrive_views.py add_users_to_gdrive()] {number_of_entries} total multiple entries detected")
            for index in range(number_of_entries):
                gmail = post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY][index]
                logger.info(f"[administration/gdrive_views.py add_users_to_gdrive()] processing user {gmail}")
                success, name, error_message = add_user_to_gdrive(gdrive,
                                                                  post_dict[GOOGLE_DRIVE_USERS_NAME_KEY][index],
                                                                  post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY][index],
                                                                  post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY][index]
                                                                  )
                if not success:
                    if 'error_message' in request.session:
                        request.session['error_message'] += '{}<br>'.format(error_message)
                    else:
                        request.session['error_message'] = '{}<br>'.format(error_message)
        else:
            logger.info(
                f"[administration/gdrive_views.py add_users_to_gdrive()] "
                f"only one user detected: {post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY]}"
            )
            success, name, error_message = add_user_to_gdrive(
                gdrive,
                post_dict[GOOGLE_DRIVE_USERS_NAME_KEY],
                post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY],
                post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY]
            )
            if not success:
                request.session['error_message'] = '{}<br>'.format(error_message)
    return HttpResponseRedirect('/administration/resources/gdrive/')


def add_user_to_gdrive(gdrive, user_legal_name, user_inputted_file_id, user_inputted_gmail):
    file_id = settings.GDRIVE_ROOT_FOLDER_ID \
        if user_inputted_file_id == "" \
        else user_inputted_file_id
    if user_does_not_have_access_to_file(user_inputted_gmail, file_id):
        successful, name, error_message = gdrive.add_users_gdrive([user_inputted_gmail], file_id)
        if successful:
            GDriveUser(
                name=user_legal_name,
                gmail=user_inputted_gmail,
                file_id=file_id,
                file_name=name
            ).save()
            return True, name, error_message
        else:
            # display the error in `file_name_or_error_message` on front-end
            logger.error("[administration/gdrive_views.py add_user_to_gdrive()] experienced following "
                         f"error when adding user to file\n{error_message}")
            return False, name, error_message
    else:
        logger.info(
            f"[administration/gdrive_views.py add_user_to_gdrive()] {user_inputted_gmail}'s access "
            "already exists")
    return True, None, None


def update_permissions_for_existing_gdrive_user(request):
    logger.info(
        f"[administration/gdrive_views.py update_permissions_for_existing_gdrive_user()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        if 'action' in request.POST:
            if request.POST['action'] == 'update':
                logger.info(
                    f"[administration/gdrive_views.py update_permissions_for_existing_gdrive_user()] processing an update")
                gdrive_user = GDriveUser.objects.get(id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                file_id = settings.GDRIVE_ROOT_FOLDER_ID \
                    if request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY] == "" \
                    else request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]
                if gdrive_user.gmail != request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY] and gdrive_user.file_id != \
                        request.POST[
                            GOOGLE_DRIVE_USERS_FILE_ID_KEY]:
                    logger.info(
                        f"[administration/gdrive_views.py update_permissions_for_existing_gdrive_user()] replacing gmail {gdrive_user.gmail}'s "
                        f"access to {gdrive_user.file_id} with {request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]} access to "
                        f"{request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]}")
                    gdrive.remove_users_gdrive([gdrive_user.gmail], gdrive_user.file_id)
                    time.sleep(5)  # if I do not put this in, the line after this one does not take effect
                    success, file_name, error_message = gdrive.add_users_gdrive(
                        [request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]],
                        file_id)
                elif gdrive_user.gmail != request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]:
                    logger.info(
                        f"[administration/gdrive_views.py update_permissions_for_existing_gdrive_user()] replacing gmail"
                        f" {gdrive_user.gmail}'s with {request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]} for user {gdrive_user.id}")
                    gdrive.remove_users_gdrive([gdrive_user.gmail], request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
                    time.sleep(5)  # if I do not put this in, the line after this one does not take effect
                    success, file_name, error_message = gdrive.add_users_gdrive(
                        [request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]],
                        file_id)
                elif gdrive_user.file_id != request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]:
                    logger.info(
                        f"[administration/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                        f"replacing file {gdrive_user.file_id}'s with {request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]} for user {gdrive_user.id}")
                    gdrive.remove_users_gdrive([gdrive_user.gmail], gdrive_user.file_id)
                    time.sleep(5)  # if I do not put this in, the line after this one does not take effect
                    success, file_name, error_message = gdrive.add_users_gdrive([gdrive_user.gmail], file_id)
                if success:
                    gdrive_user.legal_name = request.POST[GOOGLE_DRIVE_USERS_NAME_KEY]
                    gdrive_user.gmail = request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]
                    gdrive_user.file_id = file_id
                    gdrive_user.file_name = file_name
                    gdrive_user.save()
                else:
                    request.session['error_message'] = '{}<br>'.format(error_message)
            elif request.POST['action'] == 'delete':
                gdrive_user = GDriveUser.objects.get(id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                logger.info(
                    f"[administration/gdrive_views.py update_permissions_for_existing_gdrive_user()] removing {gdrive_user.id}/{gdrive_user.gmail}'s file access")
                gdrive.remove_users_gdrive([gdrive_user.gmail], gdrive_user.file_id)
                gdrive_user.delete()
    return HttpResponseRedirect('/administration/resources/gdrive/')


def make_folders_public_gdrive(request):
    logger.info(
        f"[administration/gdrive_views.py make_folder_public_gdrive()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        post_dict = parser.parse(request.POST.urlencode())
        if there_are_multiple_entries(post_dict, GOOGLE_DRIVE_USERS_FILE_ID_KEY):
            number_of_entries = len(post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
            logger.info(
                f"[administration/gdrive_views.py make_folder_public_gdrive()] {number_of_entries} total multiple entries detected")
            for index in range(number_of_entries):
                success, result = make_folder_public_gdrive(gdrive, post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY][index])
                if not success:
                    if 'error_message' in request.session:
                        request.session['error_message'] += '{}<br>'.format(result)
                    else:
                        request.session['error_message'] = '{}<br>'.format(result)
        else:
            success, result = make_folder_public_gdrive(gdrive, post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
            if not success:
                if 'error_message' in request.session:
                    request.session['error_message'] += '{}<br>'.format(result)
                else:
                    request.session['error_message'] = '{}<br>'.format(result)
    return HttpResponseRedirect('/administration/resources/gdrive/')


def make_folder_public_gdrive(gdrive, user_inputted_file_id):
    if not google_drive_file_is_publicly_available(user_inputted_file_id):
        success, file_name, file_link, error_message = gdrive.make_public_link_gdrive(user_inputted_file_id)
        if success:
            logger.info(
                f"[administration/gdrive_views.py make_folder_public_gdrive()]"
                f" processing file {user_inputted_file_id}")
            GDrivePublicFile(
                file_id=user_inputted_file_id,
                file_name=file_name,
                link=file_link
            ).save()
            return True, None
        else:
            return False, error_message
    else:
        logger.info(
            f"[administration/gdrive_views.py make_folder_public_gdrive()] file"
            f" {user_inputted_file_id} is already publicly available"
        )
        return False, f"Files {user_inputted_file_id} is already publicly available"


def update_gdrive_public_links(request):
    logger.info(
        f"[administration/gdrive_views.py update_gdrive_public_links()] request.POST={request.POST}")
    (render_value, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        if 'action' in request.POST:
            if request.POST['action'] == 'update':
                logger.info(
                    f"[administration/gdrive_views.py update_gdrive_public_links()] processing an update")
                gdrive_public_files = GDrivePublicFile.objects.get(id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                if gdrive_public_files.file_id != request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]:
                    logger.info(
                        f"[administration/gdrive_views.py update_gdrive_public_links()] updating public link {gdrive_public_files.file_id}"
                        f"to file {request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]}")

                    gdrive.remove_public_link_gdrive(gdrive_public_files.file_id)
                    success, name, public_link, error_message = gdrive.make_public_link_gdrive(
                        request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
                    if success:
                        gdrive_public_files.file_id = request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]
                        gdrive_public_files.file_name = name
                        gdrive_public_files.link = public_link
                        gdrive_public_files.save()
                    else:
                        request.session['error_message'] = '{}<br>'.format(error_message)
            elif request.POST['action'] == 'delete':
                gdrive_public_file = GDrivePublicFile.objects.get(file_id=request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
                logger.info(
                    f"[administration/gdrive_views.py update_gdrive_public_links()] removing public file {gdrive_public_file.file_id}")
                gdrive.remove_public_link_gdrive(gdrive_public_file.file_id)
                gdrive_public_file.delete()
    return HttpResponseRedirect('/administration/resources/gdrive/')


def create_google_drive_perms():
    """
    Example of google_drive_perms
    {
        "email1@gmail.com" : [
            "file_id1", "file_id2", "file_id3"
        ],
        "email2@gmail.com" : [
            "file_id4", "file_id5", "file_id6"
        ],
        "anyoneWithLink" : [
            "file_id7", "file_id8", "file_id9"
        ],
    }
    """
    current_date = datetime.datetime.now()
    term_active = (current_date.year * 10)
    if int(current_date.month) <= 4:
        term_active += 1
    elif int(current_date.month) <= 8:
        term_active += 2
    else:
        term_active += 3
    officer_list = []
    google_drive_perms = {}
    for index in range(0, 5):
        term = Term.objects.get(term_number=term_active)
        logger.info(f"collecting the list of officers for the term with term_number {term_active}")
        naughty_officers = NaughtyOfficer.objects.all()
        current_officers = [
            officer for officer in Officer.objects.all().filter(elected_term=term)
            if officer.name not in [name.strip() for name in naughty_officers.name]
        ]
        logger.info(f"current_officers retrieved = {current_officers}")
        officer_list.extend(current_officers)
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
    logger.info(f"adding gmail sfucsss@gmail.com to root folder {settings.GDRIVE_ROOT_FOLDER_ID}")
    google_drive_perms["sfucsss@gmail.com"] = settings.GDRIVE_ROOT_FOLDER_ID
    for officer in officer_list:
        if officer.gmail not in google_drive_perms.keys() and officer.gmail != "":
            google_drive_perms[officer.gmail.lower()] = [settings.GDRIVE_ROOT_FOLDER_ID]
            logger.info(f"adding gmail {officer.gmail.lower()} to root folder {settings.GDRIVE_ROOT_FOLDER_ID}")
    non_officer_users_with_access = GDriveUser.objects.all()
    for user in non_officer_users_with_access:
        if user.gmail not in google_drive_perms.keys():
            google_drive_perms[user.gmail.lower()] = [user.file_id]
            logger.info(f"adding gmail {user.gmail.lower()} to root folder {user.file_id}")
        else:
            google_drive_perms[user.gmail.lower()].append(user.file_id)
            logger.info(f"adding gmail {user.gmail.lower()} to root folder {user.file_id}")
    return google_drive_perms
