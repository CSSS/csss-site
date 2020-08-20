import logging
import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from about.models import Officer, Term
from resource_management.models import NonOfficerGoogleDriveUser, GoogleDrivePublicFile
from resource_management.models import NaughtyOfficer
from .resource_apis.gdrive.gdrive_api import GoogleDrive
from csss.views_helper import there_are_multiple_entries, verify_access_logged_user_and_create_context, \
    ERROR_MESSAGE_KEY, get_current_term

logger = logging.getLogger('csss_site')

GOOGLE_DRIVE_USERS_DB_RECORD_KEY = 'record_id'
GOOGLE_DRIVE_USERS_NAME_KEY = 'legal_name'
GOOGLE_DRIVE_USERS_GMAIL_KEY = 'gmail'
GOOGLE_DRIVE_USERS_FILE_ID_KEY = 'file_id'
GOOGLE_DRIVE_USERS_FILE_NAME_KEY = 'file_name'
GOOGLE_DRIVE_USERS_FILE_LINK_KEY = 'file_link'
TAB_STRING = 'administration'


def user_does_not_have_access_to_file(gmail, file_id):
    return len(NonOfficerGoogleDriveUser.objects.filter(
        gmail=gmail,
        file_id=file_id
    )) == 0


def google_drive_file_is_publicly_available(file_id):
    return len(GoogleDrivePublicFile.objects.filter(
        file_id=file_id
    )) > 0


def gdrive_index(request):
    """Shows the main page for google drive permission management
    """
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    if ERROR_MESSAGE_KEY in request.session:
        context['error_experienced'] = request.session[ERROR_MESSAGE_KEY].split("<br>")
        del request.session[ERROR_MESSAGE_KEY]
    context['g_drive_users'] = NonOfficerGoogleDriveUser.objects.all().filter().order_by('id')
    context['g_drive_public_links'] = GoogleDrivePublicFile.objects.all().filter().order_by('id')
    context['GOOGLE_DRIVE_USERS_DB_RECORD_KEY'] = GOOGLE_DRIVE_USERS_DB_RECORD_KEY
    context['GOOGLE_DRIVE_USERS_NAME_KEY'] = GOOGLE_DRIVE_USERS_NAME_KEY
    context['GOOGLE_DRIVE_USERS_GMAIL_KEY'] = GOOGLE_DRIVE_USERS_GMAIL_KEY
    context['GOOGLE_DRIVE_USERS_FILE_ID_KEY'] = GOOGLE_DRIVE_USERS_FILE_ID_KEY
    context['GOOGLE_DRIVE_USERS_FILE_NAME_KEY'] = GOOGLE_DRIVE_USERS_FILE_NAME_KEY
    context['GOOGLE_DRIVE_USERS_FILE_LINK_KEY'] = GOOGLE_DRIVE_USERS_FILE_LINK_KEY
    return render(request, 'resource_management/gdrive_management.html', context)


def add_users_to_gdrive(request):
    """Takes in the users who need to be given access to the SFU CSSS Google Drive

    """
    logger.info(f"[resource_management/gdrive_views.py add_users_to_gdrive()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        post_dict = parser.parse(request.POST.urlencode())
        if there_are_multiple_entries(post_dict, GOOGLE_DRIVE_USERS_NAME_KEY):
            number_of_entries = len(post_dict[GOOGLE_DRIVE_USERS_NAME_KEY])
            logger.info(
                f"[resource_management/gdrive_views.py add_users_to_gdrive()] {number_of_entries} "
                "total multiple entries detected"
            )
            for index in range(number_of_entries):
                gmail = post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY][index]
                logger.info(f"[resource_management/gdrive_views.py add_users_to_gdrive()] processing user {gmail}")
                success, name, error_message = add_user_to_gdrive(gdrive,
                                                                  post_dict[GOOGLE_DRIVE_USERS_NAME_KEY][index],
                                                                  post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY][index],
                                                                  post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY][index]
                                                                  )
                if not success:
                    if ERROR_MESSAGE_KEY in request.session:
                        request.session[ERROR_MESSAGE_KEY] += '{}<br>'.format(error_message)
                    else:
                        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        else:
            logger.info(
                f"[resource_management/gdrive_views.py add_users_to_gdrive()] "
                f"only one user detected: {post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY]}"
            )
            success, name, error_message = add_user_to_gdrive(
                gdrive,
                post_dict[GOOGLE_DRIVE_USERS_NAME_KEY],
                post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY],
                post_dict[GOOGLE_DRIVE_USERS_GMAIL_KEY]
            )
            if not success:
                request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/gdrive/')


def add_user_to_gdrive(gdrive, user_legal_name, user_inputted_file_id, user_inputted_gmail):
    """Takes in a single user and give them access to the SFU CSSS Google Drive and save them in the database

    """
    file_id = settings.GDRIVE_ROOT_FOLDER_ID \
        if user_inputted_file_id == "" \
        else user_inputted_file_id
    if user_does_not_have_access_to_file(user_inputted_gmail, file_id):
        successful, name, error_message = gdrive.add_users_gdrive([user_inputted_gmail], file_id)
        if successful:
            NonOfficerGoogleDriveUser(
                name=user_legal_name,
                gmail=user_inputted_gmail,
                file_id=file_id,
                file_name=name
            ).save()
            return True, name, error_message
        else:
            # display the error in `file_name_or_error_message` on front-end
            logger.error("[resource_management/gdrive_views.py add_user_to_gdrive()] experienced following "
                         f"error when adding user to file\n{error_message}")
            return False, name, error_message
    else:
        logger.info(
            f"[resource_management/gdrive_views.py add_user_to_gdrive()] {user_inputted_gmail}'s access "
            "already exists")
    return True, None, None


def update_permissions_for_existing_gdrive_user(request):
    """updates the permission for an existing google drive user

    """
    logger.info(
        "[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
        f"request.POST={request.POST}"
    )
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        if 'action' in request.POST:
            if request.POST['action'] == 'update':
                logger.info(
                    "[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                    "processing an update"
                )
                gdrive_user = NonOfficerGoogleDriveUser.objects.get(id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                file_id = settings.GDRIVE_ROOT_FOLDER_ID \
                    if request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY] == "" \
                    else request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]
                if gdrive_user.gmail != request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY] and gdrive_user.file_id != \
                        request.POST[
                            GOOGLE_DRIVE_USERS_FILE_ID_KEY]:
                    logger.info(
                        f"[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                        f"replacing gmail {gdrive_user.gmail}'s "
                        f"access to {gdrive_user.file_id} with {request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]} "
                        f"access to {request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]}"
                    )
                    gdrive.remove_users_gdrive([gdrive_user.gmail], gdrive_user.file_id)
                    time.sleep(5)  # if I do not put this in, the line after this one does not take effect
                    success, file_name, error_message = gdrive.add_users_gdrive(
                        [request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]],
                        file_id)
                elif gdrive_user.gmail != request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]:
                    logger.info(
                        f"[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                        f"replacing gmail {gdrive_user.gmail}'s with {request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]} "
                        f"for user {gdrive_user.id}"
                    )
                    gdrive.remove_users_gdrive([gdrive_user.gmail], request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
                    time.sleep(5)  # if I do not put this in, the line after this one does not take effect
                    success, file_name, error_message = gdrive.add_users_gdrive(
                        [request.POST[GOOGLE_DRIVE_USERS_GMAIL_KEY]],
                        file_id)
                elif gdrive_user.file_id != request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]:
                    logger.info(
                        f"[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                        f"replacing file {gdrive_user.file_id}'s with {request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]} "
                        f"for user {gdrive_user.id}"
                    )
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
                    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
            elif request.POST['action'] == 'delete':
                gdrive_user = NonOfficerGoogleDriveUser.objects.get(id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                logger.info(
                    "[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                    f"removing {gdrive_user.id}/{gdrive_user.gmail}'s file access"
                )
                gdrive.remove_users_gdrive([gdrive_user.gmail], gdrive_user.file_id)
                gdrive_user.delete()
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/gdrive/')


def make_folders_public_gdrive(request):
    """makes a list of requested google drive folders publicly available

    """
    logger.info(
        f"[resource_management/gdrive_views.py make_folders_public_gdrive()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        post_dict = parser.parse(request.POST.urlencode())
        if there_are_multiple_entries(post_dict, GOOGLE_DRIVE_USERS_FILE_ID_KEY):
            number_of_entries = len(post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
            logger.info(
                f"[resource_management/gdrive_views.py make_folders_public_gdrive()] {number_of_entries} "
                "total multiple entries detected"
            )
            for index in range(number_of_entries):
                success, result = make_folder_public_gdrive(gdrive, post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY][index])
                if not success:
                    if ERROR_MESSAGE_KEY in request.session:
                        request.session[ERROR_MESSAGE_KEY] += '{}<br>'.format(result)
                    else:
                        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(result)
        else:
            success, result = make_folder_public_gdrive(gdrive, post_dict[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
            if not success:
                if ERROR_MESSAGE_KEY in request.session:
                    request.session[ERROR_MESSAGE_KEY] += '{}<br>'.format(result)
                else:
                    request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(result)
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/gdrive/')


def make_folder_public_gdrive(gdrive, user_inputted_file_id):
    """Makes a google drive folder publicly available

    """
    if not google_drive_file_is_publicly_available(user_inputted_file_id):
        success, file_name, file_link, error_message = gdrive.make_public_link_gdrive(user_inputted_file_id)
        if success:
            logger.info(
                f"[resource_management/gdrive_views.py make_folder_public_gdrive()]"
                f" processing file {user_inputted_file_id}")
            GoogleDrivePublicFile(
                file_id=user_inputted_file_id,
                file_name=file_name,
                link=file_link
            ).save()
            return True, None
        else:
            return False, error_message
    else:
        logger.info(
            f"[resource_management/gdrive_views.py make_folder_public_gdrive()] file"
            f" {user_inputted_file_id} is already publicly available"
        )
        return False, f"Files {user_inputted_file_id} is already publicly available"


def update_gdrive_public_links(request):
    """updates an existing google drive public file
    """
    logger.info(
        f"[resource_management/gdrive_views.py update_gdrive_public_links()] request.POST={request.POST}")
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:  # if the user accessing the page is not authorized to access it
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    gdrive = GoogleDrive(settings.GDRIVE_TOKEN_LOCATION, settings.GDRIVE_ROOT_FOLDER_ID)
    if gdrive.connection_successful:
        if 'action' in request.POST:
            if request.POST['action'] == 'update':
                logger.info(
                    "[resource_management/gdrive_views.py update_gdrive_public_links()] processing an update"
                )
                gdrive_public_files = GoogleDrivePublicFile.objects.get(
                    id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                if gdrive_public_files.file_id != request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY]:
                    logger.info(
                        "[resource_management/gdrive_views.py update_gdrive_public_links()] "
                        f"updating public link {gdrive_public_files.file_id}"
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
                        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
            elif request.POST['action'] == 'delete':
                gdrive_public_file = GoogleDrivePublicFile.objects.get(
                    file_id=request.POST[GOOGLE_DRIVE_USERS_FILE_ID_KEY])
                logger.info(
                    f"[resource_management/gdrive_views.py update_gdrive_public_links()] removing "
                    f"public file {gdrive_public_file.file_id}"
                )
                gdrive.remove_public_link_gdrive(gdrive_public_file.file_id)
                gdrive_public_file.delete()
    return HttpResponseRedirect(f'{settings.URL_ROOT}resource_management/gdrive/')


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
    term_active = get_current_term()
    officer_list = []
    google_drive_perms = {}
    for index in range(0, 5):
        term = Term.objects.get(term_number=term_active)
        logger.info(
            f"[resource_management/gdrive_views.py create_google_drive_perms()] collecting the "
            f"list of officers for the term with term_number {term_active}"
        )
        naughty_officers = NaughtyOfficer.objects.all()
        current_officers = [
            officer for officer in Officer.objects.all().filter(elected_term=term)
            if officer.name not in [name.strip() for name in naughty_officers.name]
        ]
        logger.info(
            "[resource_management/gdrive_views.py create_google_drive_perms()] current_officers retrieved"
            f" = {current_officers}"
        )
        officer_list.extend(current_officers)
        if (term_active % 10) == 3:
            term_active -= 1
        elif (term_active % 10) == 2:
            term_active -= 1
        elif (term_active % 10) == 1:
            term_active -= 8
    logger.info(
        "[resource_management/gdrive_views.py create_google_drive_perms()] adding gmail sfucsss@gmail.com "
        f"to root folder {settings.GDRIVE_ROOT_FOLDER_ID}"
    )
    google_drive_perms["sfucsss@gmail.com"] = settings.GDRIVE_ROOT_FOLDER_ID
    for officer in officer_list:
        if officer.gmail not in google_drive_perms.keys() and officer.gmail != "":
            google_drive_perms[officer.gmail.lower()] = [settings.GDRIVE_ROOT_FOLDER_ID]
            logger.info(
                f"[resource_management/gdrive_views.py create_google_drive_perms()] "
                f"adding gmail {officer.gmail.lower()} to root folder {settings.GDRIVE_ROOT_FOLDER_ID}"
            )
    non_officer_users_with_access = NonOfficerGoogleDriveUser.objects.all()
    for user in non_officer_users_with_access:
        if user.gmail not in google_drive_perms.keys():
            google_drive_perms[user.gmail.lower()] = [user.file_id]
            logger.info(
                f"[resource_management/gdrive_views.py create_google_drive_perms()] "
                f"adding gmail {user.gmail.lower()} to root folder {user.file_id}"
            )
        else:
            google_drive_perms[user.gmail.lower()].append(user.file_id)
            logger.info(
                f"[resource_management/gdrive_views.py create_google_drive_perms()] "
                f"adding gmail {user.gmail.lower()} to root folder {user.file_id}"
            )
    return google_drive_perms
