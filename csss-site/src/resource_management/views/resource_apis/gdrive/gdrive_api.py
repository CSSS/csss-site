import json
import os
import pickle
import time

import googleapiclient
from django.conf import settings
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from csss.setup_logger import Loggers
from csss.views.send_email import send_email
from csss.views_helper import get_current_date
from resource_management.models import GoogleDriveRootFolderBadAccess, GoogleDriveNonMediaFileType, MediaToBeMoved

mime_type = [
    'application/vnd.google-apps.audio',
    'application/vnd.google-apps.document',
    'application/vnd.google-apps.drawing',
    'application/vnd.google-apps.file',
    'application/vnd.google-apps.folder',
    'application/vnd.google-apps.form',
    'application/vnd.google-apps.fusiontable',
    'application/vnd.google-apps.map',
    'application/vnd.google-apps.photo',
    'application/vnd.google-apps.presentation',
    'application/vnd.google-apps.site',
    'application/vnd.google-apps.script',
    'application/vnd.google-apps.spreadsheet',
    'application/vnd.google-apps.unknown',
    'application/vnd.google-apps.video',
    'application/vnd.google-apps.drive-sdk'
]

MAIN_TEAM_DRIVE_NAME = "CSSS@SFU"
PUBLIC_GALLERY_TEAM_DRIVE_FOLDER_NAME = "Public Gallery"
PRIVATE_GALLERY_TEAM_DRIVE_FOLDER_NAME = "Private Gallery"
DEEP_EXEC_TEAM_DRIVE_NAME = "Deep-Exec"

GOOGLE_DRIVE_WORKSPACE_FOLDERS = {
    MAIN_TEAM_DRIVE_NAME: {
        "folder_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS,
        "drive_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_GENERAL_DOCUMENTS
    },
    PUBLIC_GALLERY_TEAM_DRIVE_FOLDER_NAME: {
        "folder_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY,
        "drive_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PUBLIC_GALLERY
    },
    PRIVATE_GALLERY_TEAM_DRIVE_FOLDER_NAME: {
        "folder_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PRIVATE_GALLERY,
        "drive_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_ID_FOR_PRIVATE_GALLERY
    },
    DEEP_EXEC_TEAM_DRIVE_NAME: {
        "folder_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC,
        "drive_id": settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_DEEP_EXEC
    }
}


class GoogleDriveTokenCreator:
    def __init__(self, token_location, gdrive_client_id_json, scopes):
        """Create the token used by the website

        Keyword Arguments:
        token_location -- the location the token needs to be saved to
        gdrive_client_id_json -- the credentials needed to create the token
        scopes -- the scope of the permissions the token allows the site to run its command as
        """
        if settings.DEBUG == "true":
            flow = InstalledAppFlow.from_client_secrets_file(
                gdrive_client_id_json,
                scopes
            )
            creds = flow.run_local_server()
            with open(token_location, 'wb') as token:
                pickle.dump(creds, token)


class GoogleDrive:

    def __init__(self, root_file_id, token_location=None):
        self.logger = Loggers.get_logger()
        self.non_media_mimeTypes = None
        self.file_types = None
        self.make_changes = True
        self.latest_date_check = get_current_date()
        creds = None
        self.error_message = None
        self.root_file_id = root_file_id
        self.folder_or_drive_name = None
        for key, value in GOOGLE_DRIVE_WORKSPACE_FOLDERS.items():
            if value['folder_id'] == root_file_id:
                self.folder_or_drive_name = key
        if self.folder_or_drive_name is None:
            self.error_message = f'File id of {root_file_id} does not map to any known Google Workspace folders'
            return
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.connection_successful = False
        if token_location is None:
            token_location = settings.GDRIVE_TOKEN_LOCATION
        try:
            if os.path.exists(token_location):
                with open(token_location, 'rb') as token:
                    creds = pickle.load(token)
        except EOFError as e:
            self.error_message = "encountered following error when trying to read" \
                                 f" from {token_location} for google drive\n{e}"
            self.logger.error(
                f"[GoogleDrive __init__()] {self.error_message}")
            return
        except pickle.UnpicklingError as e:
            self.error_message = "encountered following error when trying to " \
                                 f"validate the token {token_location} for google drive\n{e}"
            self.logger.error(f"[GoogleDrive __init__()] {self.error_message} ")
            return
        else:
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    self.error_message = "no token detected at location" \
                                         f" \"{token_location}\" for google drive, please create locally " \
                                         "and then upload to that location. "
                    self.logger.error(f"[GoogleDrive __init__()] {self.error_message} ")
                    return
                with open(token_location, 'wb') as token:
                    pickle.dump(creds, token)

        self.gdrive = build('drive', 'v3', credentials=creds)
        self.connection_successful = True

    def add_users_gdrive(self, users, file_id=None):
        """Gives the specified users permission to the either the root file or the user specified file

        Keyword Arguments:
        users -- the list of emails who need access given to a specific file/folder
        file_id -- if specified, indicates what file/folder the users need to be given access to

        return
        success -- true or false bool
        file_name -- the name of the file/folder that the users were given access to
        e -- error that occurred if success is false
        """
        if self.connection_successful:
            if file_id is None:
                file_id = self.root_file_id
            try:
                response = self.gdrive.files().get(fileId=file_id, supportsAllDrives=True).execute()
            except googleapiclient.errors.HttpError as e:
                return False, None, f"{e}"

            file_name = response['name']
            message = ''
            if file_id is not self.root_file_id:
                message += 'a subfolder in '
            message += f'the SFU CSSS Google Workspace "{self.folder_or_drive_name}" Folder/Shared Drive'
            for user in users:
                email_message = (
                    f"Hello {user},"
                    f"You have been granted access to {message}.\n\n<br><br>"
                    "Please be careful when deleting as you have \"master\" access, as do all the officers."
                    "\n\n<br><br>-Your Sys Admin"
                )
                body = {'role': 'fileOrganizer', 'type': 'user', 'emailAddress': user.lower()}
                try:
                    self.logger.info(
                        f"[GoogleDrive add_users_gdrive()] attempting to give {user.lower()} "
                        f"permission to access the {self.folder_or_drive_name}"
                    )
                    if self.make_changes:
                        self.gdrive.permissions().create(
                            fileId=file_id,
                            emailMessage=email_message,
                            sendNotificationEmail=True,
                            body=body,
                            supportsAllDrives=True
                        ).execute()
                        time.sleep(30)
                    self.logger.info(
                        f"[GoogleDrive add_users_gdrive()] email sent to {user.lower()} "
                        "regarding their access to the sfu google drive"
                    )
                except Exception as e:
                    error_message = "Error when granting google drive access : "
                    try:
                        error_message += json.loads(e.content.decode('utf8').replace("'", '"'))['error']['message']
                    except Exception as decoding_error:
                        self.logger.error(
                            f"[GoogleDrive add_users_gdrive()] unable to parse error "
                            f"due to error {decoding_error}"
                        )
                        error_message += f"{e}"
                    self.logger.error(
                        "[GoogleDrive add_users_gdrive()] was not able to given write permission "
                        f"to {user.lower()} for {self.folder_or_drive_name}. following error occured"
                        f"instead. \n {error_message}"
                    )
                    return False, None, f"{error_message}"
            return True, file_name, None

    def remove_users_gdrive(self, users, file_id=None):
        """will remove the specified users' access to the a csss google drive folder/file

        Keyword Arguments:
        users -- list of users who need their access to the specified file removed
        file_id -- if specified, indicates what file/folder the users need to have their access removed from.
        """
        if self.connection_successful:
            if file_id is None:
                file_id = self.root_file_id
            try:
                self.logger.info(
                    "[GoogleDrive remove_users_gdrive()] attempting to get the list of permisisons for "
                    f"file with id {file_id}"
                )
                permissions = self.gdrive.permissions().list(
                    fileId=file_id, fields='permissions', supportsAllDrives=True
                ).execute()
                self.logger.info("[GoogleDrive remove_users_gdrive()] was able to get the list of file permissions")
                for user in users:
                    if user != 'csss@sfucsss.org':
                        self.logger.info(f"[GoogleDrive remove_users_gdrive()] iterating through user {user}")
                        for permission in permissions['permissions']:
                            self.logger.info(
                                f"[GoogleDrive remove_users_gdrive()] iterating through permission "
                                f"{permission}"
                            )
                            if permission['emailAddress'].lower() == user:
                                try:
                                    self.logger.info(
                                        f"[GoogleDrive remove_users_gdrive()] attempting to remove user {user}'s "
                                        f"access to file with id {file_id}"
                                    )
                                    if self.make_changes:
                                        resp = self.gdrive.permissions().delete(
                                            fileId=file_id,
                                            permissionId=permission['id'],
                                            supportsAllDrives=True
                                        ).execute()
                                        if resp != "":
                                            google_drive_bad_access = \
                                                GoogleDriveRootFolderBadAccess.objects.all.filter(
                                                    file_id=file_id
                                                ).first()
                                            if google_drive_bad_access is None:
                                                google_drive_bad_access = GoogleDriveRootFolderBadAccess(
                                                    user=user, file_id=file_id
                                                )
                                            google_drive_bad_access.number_of_nags += 1
                                            google_drive_bad_access.latest_date_check = self.latest_date_check
                                            google_drive_bad_access.save()
                                        time.sleep(30)
                                    self.logger.info("[GoogleDrive remove_users_gdrive()] attempt successful")
                                except Exception as e:
                                    self.logger.error(
                                        "[GoogleDrive remove_users_gdrive()] encountered following error "
                                        f"with permission removed. \n {e}"
                                    )
                    else:
                        self.logger.info(f"[GoogleDrive remove_users_gdrive()] skipping root user of {user}")
            except Exception as e:
                self.logger.error(
                    "[GoogleDrive remove_users_gdrive()] encountred the following error when trying "
                    f"to get the list of permissions. \n{e}"
                )

    def make_public_link_gdrive(self, file_id):
        """Create a public-link for a CSSS Google Drive Folder/File

        Keyword Arguments:
        file_id -- the file that needs to have its contents be link-share enabled.
        """
        if self.connection_successful:
            if file_id is None:
                self.logger.warning("[GoogleDrive make_public_link_gdrive()] Please specify a valid file_id")
                return False, None, None
            body = {'role': 'writer', 'type': 'anyone'}
            try:
                self.logger.info(
                    f"[GoogleDrive make_public_link_gdrive()] will attempt to make the file with id {file_id} "
                    f"publicly available."
                )
                self.gdrive.permissions().create(fileId=file_id, body=body, supportsAllDrives=True).execute()
                time.sleep(30)
                self.logger.info(
                    "[GoogleDrive make_public_link_gdrive()] will attempt to get the public link to file."
                )
                response = self.gdrive.files().get(
                    fileId=file_id, fields='name, webViewLink',
                    supportsAllDrives=True
                ).execute()
                return True, response['name'], response['webViewLink'], None
            except Exception as e:
                self.logger.error(f"[GoogleDrive make_public_link_gdrive()] encountered the following error. \n {e}")
                return False, None, None, e

    def remove_public_link_gdrive(self, file_id):
        """remove a public-link that has been enabled for the file

        Keyword Arguments:
        file_id -- the file id of the file whose public-link needs to be disabled
        """
        if self.connection_successful:
            try:
                self.logger.info(
                    "[GoogleDrive remove_public_link_gdrive()] will attempt to remove the public link "
                    f"that is enabled for file with id {file_id}"
                )
                self.gdrive.permissions().delete(
                    fileId=file_id, permissionId='anyoneWithLink',
                    supportsAllDrives=True
                ).execute()
                time.sleep(30)
                self.logger.info(
                    f"[GoogleDrive remove_public_link_gdrive()] removed public link for file with id {file_id}"
                )
            except Exception as e:
                self.logger.error(
                    "[GoogleDrive remove_public_link_gdrive()] experienced the following error when "
                    f"attempting to removing public link for file with id {file_id}.\n {e}"
                )

    def validate_ownerships_and_permissions(self, google_drive_perms):
        """
        calls methods that are responsible for ensuring that the permissions to root folder are accurate
        as well as  the ownership and permissions of its subfiles and folders are accurate as well

        Keyword Argument
         google_drive_perms -- a dict that list all the permissions that currently need to be set
        """
        self.latest_date_check = get_current_date()
        if self.root_file_id == GOOGLE_DRIVE_WORKSPACE_FOLDERS[MAIN_TEAM_DRIVE_NAME]['folder_id']:
            self.file_types = GoogleDriveNonMediaFileType.objects.all()
            self.non_media_mimeTypes = [
                file_type.mime_type for file_type in self.file_types if file_type.file_extension == ""
            ]
            MediaToBeMoved.objects.all().delete()
        self._ensure_root_permissions_are_correct(google_drive_perms)
        self._validate_individual_file_and_folder_ownership_and_permissions("CSSS", google_drive_perms)
        if self.root_file_id == GOOGLE_DRIVE_WORKSPACE_FOLDERS[MAIN_TEAM_DRIVE_NAME]['folder_id']:
            new_media_objects = MediaToBeMoved.objects.all().filter(processed=False)
            if len(new_media_objects) > 0:
                body = "https://sfucsss.org/resource_management/media_to_be_moved\n<br>\n<br>"
                for media in new_media_objects:
                    body += f"[{media.file_path/media.file_name}]({media.parent_folder_link})\n<br>"
                    media.processed = True
                    media.save()
                send_email(
                   "Media has been upload to the Google Drive that has to be moved",
                   body, "csss-sysadmin@sfu.ca", "jace"
                )
        # self._send_notifications_for_files_with_incorrect_ownership(files_to_email_owner_about)

    def _ensure_root_permissions_are_correct(self, google_drive_perms):
        """Attempts to make sure that only officers [and other necessary individuals] have access to the CSSS root folder

        Keyword Arguments:
        google_drive_perms -- a dict that list all the permissions that currently need to be set

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
        if self.connection_successful:
            try:
                response = self.gdrive.files().get(
                    fileId=self.root_file_id, fields='*', supportsAllDrives=True
                ).execute()
            except Exception as e:
                self.logger.error(
                    "[GoogleDrive _ensure_root_permissions_are_correct()] unable to get all the files "
                    f"under root due to following error.\n {e}")
                return False
            # first doing a check for the permissions to the root folder "CSSS"
            # once the new permissions have gone through, will check each individual file to make sure
            # there is nothing else that has access that should not have it.
            gdrive_users_with_access_to_root_folder = []
            if 'permissions' in response:
                gdrive_users_with_access_to_root_folder = [
                    permission['emailAddress'].lower() for permission in response['permissions']
                ]
            elif 'permissionIds' in response:
                gdrive_users_with_access_to_root_folder = [
                    (self.gdrive.permissions().get(
                        fileId=self.root_file_id, permissionId=permission_id,
                        supportsAllDrives=True, fields='*'
                    ).execute())['emailAddress'].lower() for permission_id in response['permissionIds']
                    if permission_id != 'anyoneWithLink'
                ]

            self.logger.info("[GoogleDrive _ensure_root_permissions_are_correct()] current root permissions are: ")
            self.logger.info(json.dumps(gdrive_users_with_access_to_root_folder, indent=3))
            for gdrive_user in gdrive_users_with_access_to_root_folder:
                if gdrive_user in google_drive_perms:
                    if self.root_file_id not in google_drive_perms[gdrive_user]:
                        self.logger.info(
                            f"[GoogleDrive _ensure_root_permissions_are_correct()] user {gdrive_user} has access to"
                            " root file id but their level of access indicates it they need access to something "
                            "lower down, attempting to remove their access to the root file"
                        )
                        self.remove_users_gdrive([gdrive_user])
                else:
                    self.logger.info(
                        f"[GoogleDrive _ensure_root_permissions_are_correct()] user {gdrive_user} apparently should"
                        f" not have access at all to any folders in {self.folder_or_drive_name}. "
                        f"attempting to remove it. "
                    )
                    self.remove_users_gdrive([gdrive_user])
            for gdrive_user in google_drive_perms:
                user_should_have_access = self.root_file_id in google_drive_perms[gdrive_user]
                user_doesnt_have_access = gdrive_user not in gdrive_users_with_access_to_root_folder
                if user_should_have_access and user_doesnt_have_access:
                    self.logger.info(
                        f"[GoogleDrive _ensure_root_permissions_are_correct()] user {gdrive_user} should "
                        "have access to the root google drive folder but does not, attempting to grant "
                        "them access now."
                    )
                    self.add_users_gdrive([gdrive_user])

    def _validate_individual_file_and_folder_ownership_and_permissions(self, parent_folder, google_drive_perms,
                                                                       parent_id=None,
                                                                       files_to_email_owner_about=None):
        """Goes through each single file and folder under "CSSS" root folder and checking each file/folder to make sure
         that either it has the proper permission sets or is duplicated or its owner notified that
         they need to correct who the owner of the file is so that its permissions can be corrected

         Keyword Arguments
         parent_folder -- the parent folder for the files under parent_id
         google_drive_perms -- a dict that list all the permissions that currently need to be set
         parent_id -- the folder that needs to have its contents searched
         files_to_email_owner_about -- a dictionary of the files whose owners need to be informed
          that their permission needs to be updated

        Return
        folder_to_change -- the current dictionary of the folders whose ownership needs to be changed
        """
        if parent_id is None:
            parent_id = [self.root_file_id]
        if files_to_email_owner_about is None:
            files_to_email_owner_about = {}
        next_page_token = None
        while True:
            try:
                response = self.gdrive.files().list(
                    corpora='drive',
                    driveId=GOOGLE_DRIVE_WORKSPACE_FOLDERS[self.folder_or_drive_name]['drive_id'],
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    pageToken=next_page_token,
                    fields='*',
                    pageSize=999,
                    q=f"'{parent_id[len(parent_id) - 1]}' in parents AND trashed = false"
                ).execute()
            except Exception as e:
                self.logger.error(
                    "[GoogleDrive _validate_individual_file_and_folder_ownership_and_permissions()] "
                    f"unable to get the list of files under folder with id {parent_id[len(parent_id) - 1]}"
                    f" due to following error\n.{e}"
                )
                return
            for file in response['files']:
                self._validate_permissions_for_file(
                    parent_folder, google_drive_perms, parent_id, file
                )
                files_to_email_owner_about = self._validate_owner_for_file(
                    parent_folder,
                    google_drive_perms, parent_id, files_to_email_owner_about, file
                )
            if 'nextPageToken' not in response:
                # no more files to look at under this folder so need to go back up the recursive stack
                return files_to_email_owner_about
            next_page_token = response['nextPageToken']

    def _validate_permissions_for_file(self, parent_folder, google_drive_perms, parent_id, file):
        """
        Ensure that there are not permissions for files that should not exist

        Keyword Argument
        parent_folder -- the parent folder for the file
         google_drive_perms -- a dict that list all the permissions that currently need to be set
         parent_id -- the folder that needs to have its contents searched
         file -- the info for the file that needs to have its permissions validated

        """
        self.logger.info(
            "[GoogleDrive _validate_permissions_for_file()] ensuring that the permissions for file "
            f"{file['name']} are correct"
        )
        if self.root_file_id == GOOGLE_DRIVE_WORKSPACE_FOLDERS[MAIN_TEAM_DRIVE_NAME]['folder_id']:
            file_mime_type_and_extension_not_for_image = False
            for file_type in self.file_types.exclude(file_extension=""):
                file_mime_type_and_extension_not_for_image = file_mime_type_and_extension_not_for_image or (
                   file['mimeType'] == file_type.mime_type and
                   'fileExtension' in file and file['fileExtension'] == file_type.file_extension
                )
            file_does_not_have_to_be_moved = (
               file['mimeType'] in self.non_media_mimeTypes or file_mime_type_and_extension_not_for_image
            )
            self.logger.info(
               f"[GoogleDrive _validate_permissions_for_file()] file \"{file['name']}\" "
               f"({'True' if file['mimeType'] in self.non_media_mimeTypes else 'False'} || "
               f"{'True' if file_mime_type_and_extension_not_for_image else 'False'}"
               f") detected as an image "
            )
            if not file_does_not_have_to_be_moved:
                existing_file_obj = MediaToBeMoved.objects.all().filter(file_id=file['id'])
                if len(existing_file_obj) == 0:
                    MediaToBeMoved(
                        file_path=parent_folder, file_name=file['name'],
                        parent_folder_link=(
                            self.gdrive.files().get(
                                fileId=file['parents'][0], fields='webViewLink',
                                supportsAllDrives=True
                            ).execute()['webViewLink']
                        )
                    ).save()
                return
        # first going through all the permissions for the file to ensure
        # that they are correct according to the
        # google drive perms dictionary
        if self.root_file_id == GOOGLE_DRIVE_WORKSPACE_FOLDERS[PUBLIC_GALLERY_TEAM_DRIVE_FOLDER_NAME]['folder_id']:
            google_drive_file_that_permits_downloading = (
                not file['copyRequiresWriterPermission'] and not
                self._determine_if_file_info_belongs_to_gdrive_folder(file)
            )
            if google_drive_file_that_permits_downloading:
                self.logger.info(
                    "[GoogleDrive _validate_permissions_for_file()] attempting to remove the ability to copy the file"
                    f" '{file['name']}' without writer permission"
                )
                self.gdrive.files().update(
                    fileId=file['id'], supportsAllDrives=True, body={"copyRequiresWriterPermission": True}
                ).execute()
                self.logger.info(
                    "[GoogleDrive _validate_permissions_for_file()] was able to remove the ability to copy the file"
                    f" '{file['name']}' without writer permission"
                )
        permissions = []
        if 'permissions' in file:
            permissions = file['permissions']
        elif 'permissionIds' in file:
            for permission_id in file['permissionIds']:
                permission = self.gdrive.permissions().get(
                    fileId=file['id'], permissionId=permission_id, supportsAllDrives=True, fields='*'
                ).execute()
                permissions.append(permission)

        for permission in permissions:
            if permission['id'] == 'anyoneWithLink':
                if self.root_file_id != settings.GOOGLE_WORKSPACE_SHARED_TEAM_DRIVE_FOLDER_ID_FOR_PUBLIC_GALLERY:
                    # have to allow the anyoneWithLink for the public gallery since its public facing

                    # check files that are link-share enabled
                    if 'anyoneWithLink' not in google_drive_perms.keys():
                        # there are no link-shares enabled at this time
                        self.logger.info(
                            "[GoogleDrive _validate_permissions_for_file()] removing public "
                            f"link for file with id {file['id']} and name {file['name']}"
                        )
                        self.remove_public_link_gdrive(file['id'])
                    else:
                        if len(set(google_drive_perms['anyoneWithLink']).intersection(parent_id + [file['id']])) == 0:
                            # check to see if this particular file has not been link-share enabled or
                            # one of this particular file's parent folders have also not been link-share enabled
                            self.logger.info(
                                "[GoogleDrive _validate_permissions_for_file()] removing public "
                                f"link for file with id {file['id']} and name {file['name']}"
                            )
                            self.remove_public_link_gdrive(file['id'])
            elif 'emailAddress' in permission:
                # checking permissions that are email-shared
                email_address = permission['emailAddress'].lower()
                if email_address not in google_drive_perms.keys():
                    # this email is not supposed to have access to any of the CSSS Google Drive Resources
                    self.logger.info(
                        "[GoogleDrive _validate_permissions_for_file()] remove "
                        f"{email_address}'s access to file {file['name']}"
                    )
                    self.remove_users_gdrive([email_address], file['id'])
                else:
                    if set(google_drive_perms[email_address]).intersection(parent_id + [file['id']]) == 0:
                        # checks to see if this email is supposed to have access to either this file or
                        # one of its parent folders
                        self.logger.info(
                            "[GoogleDrive _validate_permissions_for_file()] remove "
                            f"{email_address}'s access to file {file['name']}"
                        )
                        self.remove_users_gdrive([email_address], file['id'])

    def _validate_owner_for_file(
            self, parent_folder, google_drive_perms, parent_id, files_to_email_owner_about, file):
        """
        Ensure that the permissions for the given file is sfucsss@gmail.com

        Keyword Argument
        parent_folder -- the parent folder for the files under parent_id
        google_drive_perms -- a dict that list all the permissions that currently need to be set
        parent_id -- the folder that needs to have its contents searched
        files_to_email_owner_about -- a dictionary of the files whose owners need to be informed
            that their permission needs to be updated
        file -- the info for the file that needs to have its permissions validated

        Return
        folder_to_change -- the current dictionary of the folders whose ownership needs to be changed
        """
        # valid_ownership_for_file = self._owner_of_folder_is_correct(file)
        # self.logger.debug(
        #     "[GoogleDrive _validate_owner_for_file()] file/folder "
        #     f"{file['name']} of type {file['mimeType']} with owner {file['owners'][0]['emailAddress'].lower()} "
        #     f"will {'not ' if valid_ownership_for_file else ''}have its owner be alerted."
        # )
        # if not valid_ownership_for_file:
        #     google_drive_file = GoogleDriveFileAwaitingOwnershipChange.objects.all().filter(
        #         file_id=file['id']
        #     ).first()
        #     parent_folder_link = (
        #         self.gdrive.files().get(
        #             fileId=file['parents'][0], fields='webViewLink', supportsAllDrives=True
        #         ).execute()[
        #             'webViewLink']
        #     )
        #     if google_drive_file is None:
        #         google_drive_file = GoogleDriveFileAwaitingOwnershipChange(
        #             file_id=file['id'], file_name=file['name'], file_path=parent_folder,
        #             parent_folder_link=parent_folder_link,
        #             file_owner=file['owners'][0]['emailAddress'],
        #         )
        #     google_drive_file.number_of_nags += 1
        #     google_drive_file.latest_date_check = self.latest_date_check
        #     google_drive_file.save()
        #     self.logger.info(
        #         "[GoogleDrive _validate_owner_for_file()] file/folder "
        #         f"{file['name']} of type {file['mimeType']} with owner {file['owners'][0]['emailAddress'].lower()} "
        #         f"will have its owner be alerted."
        #     )
        #     file_is_form_or_folder = (
        #         self._file_is_gdrive_form(file) or
        #         self._determine_if_file_info_belongs_to_gdrive_folder(file)
        #     )
        #     if self._file_is_gdrive_file(file) and not file_is_form_or_folder:
        #         self.logger.info(
        #             "[GoogleDrive _validate_owner_for_file()] file "
        #             f"{file['name']} determined to be a regular google drive file that is not a form"
        #         )
        #         self._alert_user_to_change_owner(file)
        #     else:
        #         file_name = file['name']
        #         self.logger.info(
        #             f"[GoogleDrive _validate_owner_for_file()] google drive file {file_name} "
        #             "determined to be a folder or form"
        #         )
        #         for owner in file['owners']:
        #             owner_email = owner['emailAddress'].lower()
        #             self.logger.info(
        #                 f"[GoogleDrive _validate_owner_for_file()] adding {owner_email} "
        #                 f"to the list of people who need to be alerted about changing "
        #                 f"ownership for folder or form {file_name}"
        #             )
        #             if owner_email in files_to_email_owner_about:
        #                 files_to_email_owner_about[owner_email]['file_infos'].append(
        #                     {
        #                         'file_name': file_name,
        #                         "containing_folder_link": parent_folder_link
        #                     }
        #                 )
        #             else:
        #                 files_to_email_owner_about[owner_email] = {
        #                     'full_name': owner['displayName'],
        #                     'file_infos': [{
        #                         'file_name': file_name,
        #                         "containing_folder_link": parent_folder_link
        #                     }]
        #                 }
        #             if not self._determine_if_file_info_belongs_to_gdrive_folder(file):
        #                 self.logger.info(
        #                     "[GoogleDrive _validate_owner_for_file()] file "
        #                     f"{file['name']} determined to probably be an uploaded file or google drive form"
        #                 )
        #                 if self._duplicate_file(file):
        #                     self._alert_user_to_delete_file(file, files_to_email_owner_about, owner_email, owner)
        # elif not self._file_is_gdrive_form(file):
        #     self._remove_outdated_comments(file)
        if self._determine_if_file_info_belongs_to_gdrive_folder(file):
            # this is a folder so we have to check to see if any of its files have a bad permission set
            return self._validate_individual_file_and_folder_ownership_and_permissions(
                f"{parent_folder}/{file['name']}",
                google_drive_perms, parent_id=parent_id + [file['id']],
                files_to_email_owner_about=files_to_email_owner_about
            )
        return files_to_email_owner_about

    # def _determine_if_file_id_belongs_to_gdrive_folder(self, file_id):
    #     """
    #     determines if the google drive file type is a folder
    #
    #     Keyword Argument
    #     file_info -- the id for the file whose type needs to be checked
    #
    #     Return
    #     Bool -- true or false to indicate if the file is a folder
    #     """
    #     file_info = self.gdrive.files().get(
    #         fields='*',
    #         fileId=file_id,
    #         supportsAllDrives=True
    #     ).execute()
    #     return self._determine_if_file_info_belongs_to_gdrive_folder(file_info)

    def _determine_if_file_info_belongs_to_gdrive_folder(self, file_info):
        """
        determines if the google drive file type is a folder

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is a folder
        """
        if 'mimeType' in file_info:
            self.logger.info(
                f"[GoogleDrive _determine_if_file_info_belongs_to_gdrive_folder()] "
                f"parsing a file_info with a type of {file_info['mimeType']} "
            )
        else:
            self.logger.error(
                "[GoogleDrive _determine_if_file_info_belongs_to_gdrive_folder()] "
                f"unable to find a file type for file {file_info['name']}"
            )
        return 'mimeType' in file_info and file_info['mimeType'] == 'application/vnd.google-apps.folder'

    # def _owner_of_folder_is_correct(self, file_info):
    #     """
    #     determines if the owner of the google drive folder is correct
    #
    #     Keyword Argument
    #     file_info -- the info for the file whose type needs to be checked
    #
    #     Return
    #     Bool -- true or false to indicate if the folder is owned by sfucsss or not
    #     """
    #     file_ownership = 'ownedByMe' in file_info and file_info['ownedByMe']
    #     if 'ownedByMe' in file_info:
    #         self.logger.info(
    #             f"[GoogleDrive _owner_of_folder_is_correct()] "
    #             f"file is {'' if file_ownership else 'not '}owned by sfucsss@gmail.com"
    #         )
    #     else:
    #         self.logger.error(
    #             "[GoogleDrive _owner_of_folder_is_correct()] "
    #             f"unable to find key 'ownedByMe' for file {file_info['name']}"
    #         )
    #     return file_ownership

    # def _file_is_gdrive_file(self, file_info):
    #     """
    #     determine if the file is a goggle-app type that can be commented on
    #
    #     Keyword Argument
    #     file_info -- the info for the file whose type needs to be checked
    #
    #     Return
    #     Bool -- true or false to indicate if the file is of google-app type that can be commented on
    #     """
    #     file_type = 'mimeType' in file_info and 'google-apps' in file_info['mimeType'] and \
    #                 file_info['mimeType'] != "application/vnd.google-apps.form"
    #     if 'mimeType' in file_info:
    #         self.logger.info(
    #             f"[GoogleDrive _file_is_gdrive_file()] file type for file {file_info['name']} "
    #             f"is {file_info['mimeType']}"
    #         )
    #     else:
    #         self.logger.error(
    #             "[GoogleDrive _file_is_gdrive_file()] "
    #             f"unable to find key 'mimeType' for file {file_info['name']}"
    #         )
    #     return file_type

    # def _file_is_gdrive_form(self, file_info):
    #     """
    #     determine if the file is a goggle form
    #
    #     Keyword Argument
    #     file_info -- the info for the file whose type needs to be checked
    #
    #     Return
    #     Bool -- true or false to indicate if the file is a google form
    #     """
    #     file_type = 'mimeType' in file_info and file_info['mimeType'] == "application/vnd.google-apps.form"
    #     if 'mimeType' in file_info:
    #         self.logger.info(
    #             f"[GoogleDrive _file_is_gdrive_file()] file type for file {file_info['name']} "
    #             f"is {file_info['mimeType']}"
    #         )
    #     else:
    #         self.logger.error(
    #             "[GoogleDrive _file_is_gdrive_file()] "
    #             f"unable to find key 'mimeType' for file {file_info['name']}"
    #         )
    #     return file_type

    # def _alert_user_to_change_owner(self, file_info):
    #     """
    #     adds a comment to the file to alert the owner that they need to change the owner of the google drive file
    #
    #     Keyword Argument
    #     file_info -- the file that needs to have the comment added to it
    #     """
    #     try:
    #         body = {'content': (
    #             "Please change owner of this file to sfucsss@gmail.com.\nInstructions for doing so can be found"
    #             " here: https://github.com/CSSS/managingCSSSResources"
    #         )}
    #         self.logger.info(
    #             "[GoogleDrive _alert_user_to_change_owner()] attempting to add a comment added "
    #             f"to file {file_info['name']}"
    #         )
    #         if self.make_changes:
    #             response = self.gdrive.comments().create(
    #                 fileId=file_info['id'], fields="*", body=body, supportsAllDrives=True
    #             ).execute()
    #             if response['content'] == body['content']:
    #                 self.logger.info(
    #                     f"[GoogleDrive _alert_user_to_change_owner()] "
    #                     f"comment added to file {file_info['name']}"
    #                 )
    #             else:
    #                 self.logger.error(
    #                     "[GoogleDrive _alert_user_to_change_owner()] unable to add comment"
    #                     f" to file {file_info['name']}"
    #                 )
    #     except Exception as e:
    #         self.logger.error(
    #             f"[GoogleDrive _alert_user_to_change_owner()] unable to add comment to file {file_info['name']} "
    #             f"of type {file_info['mimeType']} due to following error.\n{e}"
    #         )

    # def _remove_outdated_comments(self, file_info):
    #     """
    #     removes any comments made by sfucsss@gmail.com from any files whose permissions has been successfully
    #      transferred over to sfucsss@gmail.com
    #
    #     Keyword Argument
    #     file_info -- the file that needs to have its comments deleted
    #     """
    #     try:
    #         self.logger.info(
    #             "[GoogleDrive _remove_outdated_comments()] attempting to remove any comments that "
    #             f"sfucsss@gmail.com made on file {file_info['name']}"
    #         )
    #         response = self.gdrive.comments().list(
    #             fileId=file_info['id'], fields="*", supportsAllDrives=True
    #         ).execute()
    #         self.logger.info("[GoogleDrive _remove_outdated_comments()] received response from google drive API ")
    #         for comment in response['comments']:
    #             self.logger.info(f"[GoogleDrive _remove_outdated_comments()] iterating though comment {comment}")
    #             if comment['author']['me']:
    #                 if self.make_changes:
    #                     comment_response = self.gdrive.comments().delete(
    #                         commentId=comment['id'], fileId=file_info['id'],
    #                         supportsAllDrives=True
    #                     ).execute()
    #                     if comment_response != "":
    #                         self.logger.info(
    #                             f"[GoogleDrive _remove_outdated_comments()] received comment response of"
    #                             f" {comment_response}"
    #                         )
    #                         self.logger.error(
    #                             f"[GoogleDrive _remove_outdated_comments()] unable to delete outdated comment"
    #                             f" on file {file_info['name']}"
    #                         )
    #     except Exception as e:
    #         self.logger.error(
    #             f"[GoogleDrive _remove_outdated_comments()] unable to remove comments on file {file_info['name']} "
    #             f"of type {file_info['mimeType']} due to following error.\n{e}"
    #         )

    # def _duplicate_file(self, file_info):
    #     """
    #     Duplicates a non-google native document and renames the original to indicate it should no longer
    #     be used
    #
    #     Keyword Arguments:
    #     file_info -- the file_info for the file that needs to be duplicated
    #
    #     Return
    #     Bool -- true or false to indicate if the file was successfully duplicated
    #     """
    #     try:
    #         if file_info['name'] != 'DO_NOT_USE__DELETE_FILE':
    #             self.logger.info(
    #                 f"[GoogleDrive _duplicate_file()] "
    #                 f"attempting to duplicate file {file_info['name']} with id {file_info['id']}")
    #             if self.make_changes:
    #                 self.gdrive.files().copy(
    #                     fileId=file_info['id'],
    #                     fields='*',
    #                     body={'name': file_info['name']},
    #                     supportsAllDrives=True
    #                 ).execute()
    #             self.logger.info(
    #                 f"[GoogleDrive _duplicate_file()] "
    #                 f"file {file_info['name']} with id {file_info['id']} successfully duplicated")
    #             body = {'name': 'DO_NOT_USE__DELETE_FILE'}
    #             self.logger.info(
    #                 f"[GoogleDrive _duplicate_file()]  attempting to set the body "
    #                 f"for file {file_info['name']} with id {file_info['id']} to {body}")
    #             if self.make_changes:
    #                 self.gdrive.files().update(fileId=file_info['id'], body=body, supportsAllDrives=True).execute()
    #             self.logger.info(
    #                 f"[GoogleDrive _duplicate_file()] "
    #                 f"file {file_info['name']} with id {file_info['id']}'s body successfully updated")
    #         return True
    #     except Exception as e:
    #         self.logger.error(
    #             f"[GoogleDrive _duplicate_file()] "
    #             f"unable to duplicate the file due to following error.\n{e}"
    #         )
    #         return False

    # def _alert_user_to_delete_file(self, file_info, files_to_email_owner_about, owner_email, owner):
    #     """
    #     alert the owner of a file via a comment that its needs to be deleted
    #
    #     Keyword Argument
    #     file_info -- the info for the file that needs to be deleted
    #     files_to_email_owner_about -- a dictionary of the files whose owners need to be informed
    #         that their permission needs to be updated
    #     owner_email -- the email address for the current owner of the file
    #     owner -- the info of the current owner of the file
    #     """
    #     try:
    #         parent_folder_link = (
    #             self.gdrive.files().get(
    #                 fileId=file_info['parents'][0], fields='webViewLink', supportsAllDrives=True
    #             ).execute()[
    #                 'webViewLink']
    #         )
    #         files_to_email_owner_about[owner_email] = {
    #             'full_name': owner['displayName'],
    #             'file_infos': [{
    #                 'file_name': file_info['name'],
    #                 "containing_folder_link": parent_folder_link
    #             }]
    #         }
    #     except Exception as e:
    #         self.logger.error(
    #             f"[GoogleDrive _alert_user_to_delete_file()] unable to add comment to file {file_info['name']} "
    #             f"of type {file_info['mimeType']} due to following error.\n{e}"
    #         )

    # def _send_notifications_for_files_with_incorrect_ownership(self, files_to_email_owner_about):
    #     """
    #     will email all the relevant owners of the folders that they are owners of that need to have
    #     their ownership changed
    #
    #     Keyword Argument
    #     files_to_email_owner_about -- a dictionary that contains a list of all the emails and their corresponding
    #         files that they need to be made aware of that have to have their ownership changed
    #     """
    #     self.logger.info(
    #         "[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] attempting"
    #         " to setup connection to gmail server"
    #     )
    #     subject = "UPDATED_LINKS MATEY!!! SFU CSSS Google Drive Folder ownership change"
    #     body_template = (
    #         "Please change owner of the following folders and forms to sfucsss@gmail.com.\n"
    #         "Instructions for doing so can be "
    #         "found  here: https://github.com/CSSS/managingCSSSResources\n\nFolders whose ownership needs "
    #         "to be changed:\n"
    #     )
    #     officers = Officer.objects.all()
    #     gmail = Gmail()
    #     self.logger.info(
    #         "[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] "
    #         "files_to_email_owner_about="
    #     )
    #     self.logger.info(json.dumps(files_to_email_owner_about, indent=3))
    #     for to_email in files_to_email_owner_about:
    #         body = body_template + "".join(
    #             [
    #                 f"{file['file_name']} : {file['containing_folder_link']}\n" for file in
    #                 files_to_email_owner_about[to_email]['file_infos']
    #             ]
    #         )
    #         files_names = [file['file_name'] for file in files_to_email_owner_about[to_email]['file_infos']]
    #         to_name = files_to_email_owner_about[to_email]['full_name']
    #         self.logger.info(
    #             "[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] attempting to "
    #             f"send email to {to_email} about files {files_names}"
    #         )
    #         self.logger.info(
    #             "[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] "
    #             f"retrieving officer with gmail [{to_email}]"
    #         )
    #         officer = officers.filter(gmail=to_email).order_by('-start_date').first()
    #         self.logger.info(
    #             "[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] officer is "
    #             f"{'' if officer is None else 'not '}None"
    #         )
    #         if officer is not None:
    #             # send_email(
    #             #     subject, body, f"{officer.sfu_computing_id}@sfu.ca", officer.full_name, gmail=gmail
    #             # )
    #             send_discord_dm(officer.discord_id, subject, body)
    #         if self.make_changes:
    #             send_email(subject, body, to_email, to_name, gmail=gmail)
    #
    #     pending_ownership_changes = GoogleDriveFileAwaitingOwnershipChange.objects.all()
    #     pending_ownership_changes.filter(latest_date_check__lt=self.latest_date_check).delete()
    #     pending_ownership_changes = pending_ownership_changes.filter(
    #         number_of_nags__gte=6
    #     ).order_by('file_owner')
    #     overall_body = ""
    #     if len(pending_ownership_changes) > 1:
    #         overall_body += "Pending Ownership Changes\n\n"
    #     users_added_so_far = []
    #     for pending_ownership_change in pending_ownership_changes:
    #         if pending_ownership_change.file_owner not in users_added_so_far:
    #             overall_body += f"Owner: {pending_ownership_change.file_owner}:\n"
    #             users_added_so_far.append(pending_ownership_change.file_owner)
    #         overall_body += (
    #             f"\tFile: {pending_ownership_change.file_path}/{pending_ownership_change.file_name}\n"
    #             f"\tFolder Link: {pending_ownership_change.parent_folder_link}\n"
    #             f"\tNumber of Nags: {pending_ownership_change.number_of_nags}\n"
    #         )
    #
    #     pending_bad_accesses = GoogleDriveRootFolderBadAccess.objects.all()
    #     pending_bad_accesses.filter(latest_date_check__lt=self.latest_date_check).delete()
    #     pending_bad_accesses = GoogleDriveRootFolderBadAccess.objects.all().filter(
    #         number_of_nags__gte=6
    #     ).order_by('user')
    #     if len(pending_bad_accesses) > 1:
    #         overall_body += "\nPending Bad Access\n\n"
    #     users_added_so_far = []
    #     for pending_bad_access in pending_bad_accesses:
    #         if pending_bad_access.user not in users_added_so_far:
    #             overall_body += f"User: {pending_bad_access.user}:\n"
    #             users_added_so_far.append(pending_bad_access.user)
    #         overall_body += (
    #             f"\tFileID: {pending_bad_access.file_id} && Number of Nags: {pending_bad_access.number_of_nags}\n"
    #         )
    #     if len(overall_body) > 0:
    #         send_email(
    #             subject,
    #             "http://sfucsss.org/resource_management/nags\n\n" + overall_body,
    #             "csss-sysadmin@sfu.ca", "jace", gmail=gmail, attachment=self.logger.handlers[1].baseFilename
    #         )
    #     if len(MediaToBeMoved.objects.all()) > 0:
    #        send_email(
    #            "Media has been upload to the Google Drive that has to be moved",
    #            "http://sfucsss.org/resource_management/media_to_be_moved\n\n",
    #            "csss-sysadmin@sfu.ca", "jace", gmail=gmail
    #        )
    #     gmail.close_connection()
