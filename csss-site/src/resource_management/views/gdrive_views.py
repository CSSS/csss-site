import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from querystring_parser import parser

from csss.setup_logger import Loggers
from csss.views.context_creation.create_authenticated_contexts import create_context_for_google_drive_permissions
from csss.views.privilege_validation.list_of_officer_details_from_past_specified_terms import \
    get_list_of_officer_details_from_past_specified_terms
from csss.views.request_validation import validate_request_to_update_gdrive_permissions
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import there_are_multiple_entries
from resource_management.models import NonOfficerGoogleDriveUser, GoogleDrivePublicFile
from .resource_apis.gdrive.gdrive_api import GoogleDrive

GOOGLE_DRIVE_USERS_DB_RECORD_KEY = 'record_id'
GOOGLE_DRIVE_USERS_NAME_KEY = 'legal_name'
GOOGLE_DRIVE_USERS_GMAIL_KEY = 'gmail'
GOOGLE_DRIVE_USERS_FILE_ID_KEY = 'file_id'
GOOGLE_DRIVE_USERS_FILE_NAME_KEY = 'file_name'
GOOGLE_DRIVE_USERS_FILE_LINK_KEY = 'file_link'
TAB_STRING = 'administration'

ERROR_MESSAGE_KEY = 'error_message'


def user_does_not_have_access_to_file(gmail, file_id):
    """
    indicates if a user has access to a file in SFU CSSS Google Drive

    Keyword Arguments
    gmail -- the gmail belonging to the user whose access has to be determined
    file_id -- the file_id that belongs to the file that needs to be checked

    return
    Bool - true if the user has access to the file
    """
    return len(NonOfficerGoogleDriveUser.objects.filter(
        gmail=gmail,
        file_id=file_id
    )) == 0


def google_drive_file_is_publicly_available(file_id):
    """
    determines if a file is publicly available

    Keyword Arguments
    file_id -- the file_id that belongs to the file that need to be checked

    return
    Bool -- true if the file is publicly available
    """
    return len(GoogleDrivePublicFile.objects.filter(
        file_id=file_id
    )) > 0


def gdrive_index(request):
    """
    Shows the main page for google drive permission management
    """
    context = create_context_for_google_drive_permissions(request, tab=TAB_STRING)
    if ERROR_MESSAGE_KEY in request.session:
        context[ERROR_MESSAGES_KEY] = request.session[ERROR_MESSAGE_KEY].split("<br>")
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
    """
    Takes in the users who need to be given access to the SFU CSSS Google Drive
    """
    logger = Loggers.get_logger()
    logger.info(f"[resource_management/gdrive_views.py add_users_to_gdrive()] request.POST={request.POST}")
    validate_request_to_update_gdrive_permissions(request)
    gdrive = GoogleDrive(settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS)
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
    """
    Takes in a single user and give them access to the SFU CSSS Google Drive and save them in the database

    Keyword Argument
    gdrive -- the gdrive API object
    user_legal_name -- the user's full name
    user_inputted_file_id -- the file that the user needs to be given permission to
    user_inputted_gmail -- the gmail belonging to the user

    return
    Bool -- true or false depending on if the user now had access to the file
    file_name -- the name of the file that the user has to be given access to or None if unable to give the user
        access to the file
    error_message -- error if unable to give the user access to the file or None otherwise
   """
    logger = Loggers.get_logger()
    file_id = settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS \
        if user_inputted_file_id == "" \
        else user_inputted_file_id
    if user_does_not_have_access_to_file(user_inputted_gmail, file_id):
        successful, file_name, error_message = gdrive.add_users_gdrive([user_inputted_gmail], file_id)
        if successful:
            NonOfficerGoogleDriveUser(
                name=user_legal_name,
                gmail=user_inputted_gmail,
                file_id=file_id,
                file_name=file_name
            ).save()
            return True, file_name, error_message
        else:
            # display the error in `file_name_or_error_message` on front-end
            logger.error("[resource_management/gdrive_views.py add_user_to_gdrive()] experienced following "
                         f"error when adding user to file\n{error_message}")
            return False, file_name, error_message
    else:
        logger.info(
            f"[resource_management/gdrive_views.py add_user_to_gdrive()] {user_inputted_gmail}'s access "
            "already exists")
    return True, None, None


def update_permissions_for_existing_gdrive_user(request):
    """
    updates the permission for an existing google drive user
    """
    logger = Loggers.get_logger()
    logger.info(
        "[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
        f"request.POST={request.POST}"
    )
    validate_request_to_update_gdrive_permissions(request)
    gdrive = GoogleDrive(settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS)
    if gdrive.connection_successful:
        if 'action' in request.POST:
            if request.POST['action'] == 'update':
                logger.info(
                    "[resource_management/gdrive_views.py update_permissions_for_existing_gdrive_user()] "
                    "processing an update"
                )
                success = False
                file_name = None
                gdrive_user = NonOfficerGoogleDriveUser.objects.get(id=request.POST[GOOGLE_DRIVE_USERS_DB_RECORD_KEY])
                file_id = settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS \
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
    """
    makes a list of requested google drive folders publicly available
    """
    logger = Loggers.get_logger()
    logger.info(
        f"[resource_management/gdrive_views.py make_folders_public_gdrive()] request.POST={request.POST}")
    validate_request_to_update_gdrive_permissions(request)
    gdrive = GoogleDrive(settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS)
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
    """
    Makes a google drive folder publicly available

    Keyword Argument
    gdrive -- the google drive API object
    user_inputted_file_id -- the file id for the file that needs to be made publicly available

    return
    Bool -- true or false
    error_message -- None if successful and error_message if not successful
    """
    logger = Loggers.get_logger()
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
    """
    updates an existing google drive public file
    """
    logger = Loggers.get_logger()
    logger.info(
        f"[resource_management/gdrive_views.py update_gdrive_public_links()] request.POST={request.POST}")
    validate_request_to_update_gdrive_permissions(request)
    gdrive = GoogleDrive(settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS)
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


def create_google_drive_perms(root_file_id=settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS,
                              execs_only=False, relevant_previous_terms=5):
    """
    Keyword Argument
    root_file_id -- the file ID for the root folder/Shared Team drive whose permissions are needed
    execs_only -- flag to ensure that only folks who were in executive positions are returned. This is used
        in conjunction with relevant_previous_terms of 0 to get the list of current executives for `Deep-Execs` shared
        team drive
    relevant_previous_terms - if 0 specified, only get current term
        if 1 is specified get current and previous term and so forth
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
    logger = Loggers.get_logger()
    officer_list = get_list_of_officer_details_from_past_specified_terms(
        execs_only=execs_only, relevant_previous_terms=relevant_previous_terms
    )
    google_drive_perms = {}

    logger.info(
        "[resource_management/gdrive_views.py create_google_drive_perms()] adding gmail csss@sfucsss.org "
        f"to root folder {root_file_id}"
    )
    google_drive_perms['csss@sfucsss.org'] = root_file_id
    for officer in officer_list:
        if officer.gmail not in google_drive_perms.keys() and officer.gmail != "":
            google_drive_perms[officer.gmail.lower()] = [root_file_id]
            logger.info(
                f"[resource_management/gdrive_views.py create_google_drive_perms()] "
                f"adding gmail {officer.gmail.lower()} to root folder {root_file_id}"
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

    google_drive_perms['anyoneWithLink'] = [file.file_id for file in GoogleDrivePublicFile.objects.all()]

    return google_drive_perms
