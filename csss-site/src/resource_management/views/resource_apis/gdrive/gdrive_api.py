import logging
import os
import pickle
import time

import googleapiclient
from django.conf import settings

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from csss.Gmail import Gmail
from resource_management.models import GoogleMailAccountCredentials

logger = logging.getLogger('csss_site')

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

    def __init__(self, token_location, root_file_id):
        creds = None
        self.error_message = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.connection_successful = False
        try:
            if os.path.exists(token_location):
                with open(token_location, 'rb') as token:
                    creds = pickle.load(token)
        except EOFError as e:
            self.error_message = "encountered following error when trying to read" \
                                 f" from {token_location} for google drive\n{e}"
            logger.error(
                f"[GoogleDrive __init__()] {self.error_message}")
            return
        except pickle.UnpicklingError as e:
            self.error_message = "encountered following error when trying to " \
                                 f"validate the token {token_location} for google drive\n{e}"
            logger.error(f"[GoogleDrive __init__()] {self.error_message} ")
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
                    logger.error(f"[GoogleDrive __init__()] {self.error_message} ")
                    return
                with open(token_location, 'wb') as token:
                    pickle.dump(creds, token)

        self.gdrive = build('drive', 'v3', credentials=creds)
        self.root_file_id = root_file_id
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
                response = self.gdrive.files().get(fileId=file_id).execute()
            except googleapiclient.errors.HttpError as e:
                return False, None, f"{e}"

            file_name = response['name']
            if file_id is self.root_file_id:
                message = 'the root SFU CSSS Google Drive folder'
            else:
                message = 'a subfolder in the SFU CSSS Google Drive'
            for user in users:
                email_message = (
                    f"Hello {user},"
                    f"You have been granted access to {message}"
                    "Please be careful when deleting as you have \"master\" access, as do all the officers."
                    "Furthermore, when creating a file on the CSSS Google Drive, please "
                    "try to transfer ownerships of any files you create to \"sfucsss@gmail.com\" account "
                    "as this makes it easier for me to remove your access when it's time to revoke it."
                    "You can figure out how to do that with these instructions: "
                    "https://github.com/CSSS/managingCSSSResources/tree/master/google_drive"
                    "-Your Sys Admin"
                )
                body = {'role': 'writer', 'type': 'user', 'emailAddress': user.lower()}
                try:
                    logger.info(
                        f"[GoogleDrive add_users_gdrive()] attempting to give {user.lower()} "
                        "permission to access the sfu csss google drive"
                    )
                    self.gdrive.permissions().create(
                        fileId=file_id,
                        emailMessage=email_message,
                        sendNotificationEmail=True,
                        body=body
                    ).execute()
                    logger.info(
                        f"[GoogleDrive add_users_gdrive()] email sent to {user.lower()} "
                        "regarding their access to the sfu google drive"
                    )
                except Exception as e:
                    logger.error(
                        "[GoogleDrive add_users_gdrive()] was not able to given write permission "
                        f"to {user.lower()} for the SFU CSSS Google Drive. following error occured"
                        f"instead. \n {e}"
                    )
                    return False, None, f"{e}"
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
                logger.info(
                    "[GoogleDrive remove_users_gdrive()] attempting to get the list of permisisons for "
                    f"file with id {file_id}"
                )
                permissions = self.gdrive.permissions().list(fileId=file_id, fields='permissions').execute()
                logger.info("[GoogleDrive remove_users_gdrive()] was able to get the list of file permissions")
                for user in users:
                    for permission in permissions['permissions']:
                        if permission['emailAddress'].lower() == user:
                            try:
                                logger.info(
                                    f"[GoogleDrive remove_users_gdrive()] attempting to remove user {user}'s "
                                    f"access to file with id {file_id}"
                                )
                                self.gdrive.permissions().delete(fileId=file_id,
                                                                 permissionId=permission['id']).execute()
                                if self._determine_if_file_id_belongs_to_gdrive_folder(file_id):
                                    time.sleep(5)
                                logger.info("[GoogleDrive remove_users_gdrive()] attempt successful")
                            except Exception as e:
                                logger.error(
                                    "[GoogleDrive remove_users_gdrive()] encountered following error "
                                    f"with permission removed. \n {e}"
                                )
            except Exception as e:
                logger.error(
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
                logger.warning("[GoogleDrive make_public_link_gdrive()] Please specify a valid file_id")
                return False, None, None
            body = {'role': 'writer', 'type': 'anyone'}
            try:
                logger.info(
                    f"[GoogleDrive make_public_link_gdrive()] will attempt to make the file with id {file_id} "
                    f"publicly available."
                )
                self.gdrive.permissions().create(fileId=file_id, body=body).execute()
                logger.info("[GoogleDrive make_public_link_gdrive()] will attempt to get the public link to file.")
                response = self.gdrive.files().get(fileId=file_id, fields='name, webViewLink').execute()
                return True, response['name'], response['webViewLink'], None
            except Exception as e:
                logger.error(f"[GoogleDrive make_public_link_gdrive()] encountered the following error. \n {e}")
                return False, None, None, e

    def remove_public_link_gdrive(self, file_id):
        """remove a public-link that has been enabled for the file

        Keyword Arguments:
        file_id -- the file id of the file whose public-link needs to be disabled
        """
        if self.connection_successful:
            try:
                logger.info(
                    "[GoogleDrive remove_public_link_gdrive()] will attempt to remove the public link "
                    f"that is enabled for file with id {file_id}"
                )
                self.gdrive.permissions().delete(fileId=file_id, permissionId='anyoneWithLink').execute()
                logger.info(
                    f"[GoogleDrive remove_public_link_gdrive()] removed public link for file with id {file_id}"
                )
            except Exception as e:
                logger.error(
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
        self._ensure_root_permissions_are_correct(google_drive_perms)
        files_to_email_owner_about = self._validate_individual_file_and_folder_ownership_and_permissions(
            google_drive_perms
        )
        self._send_email_notifications_for_files_with_incorrect_ownership(files_to_email_owner_about)

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
                response = self.gdrive.files().get(fileId=self.root_file_id, fields='*').execute()
            except Exception as e:
                logger.error(
                    "[GoogleDrive _ensure_root_permissions_are_correct()] unable to get all the files "
                    f"under root due to following error.\n {e}")
                return False
            # first doing a check for the permissions to the root folder "CSSS"
            # once the new permissions have gone through, will check each individual file to make sure
            # there is nothing else that has access that should not have it.
            gdrive_users_with_access_to_root_folder = [
                permission['emailAddress'].lower() for permission in response['permissions']
            ]
            for gdrive_user in gdrive_users_with_access_to_root_folder:
                if gdrive_user in google_drive_perms:
                    if self.root_file_id not in google_drive_perms[gdrive_user]:
                        logger.info(
                            f"[GoogleDrive _ensure_root_permissions_are_correct()] user {gdrive_user} has access to"
                            " root file id but their level of access indicates it they need access to something "
                            "lower down, attempting to remove their access to the root file"
                        )
                        self.remove_users_gdrive([gdrive_user])
                else:
                    logger.info(
                        f"[GoogleDrive _ensure_root_permissions_are_correct()] user {gdrive_user} apparently should"
                        " not have access at all to any sfu csss google drive folder. attempting to remove it. "
                    )
                    self.remove_users_gdrive([gdrive_user])
            for gdrive_user in google_drive_perms:
                if self.root_file_id in gdrive_user and gdrive_user not in gdrive_users_with_access_to_root_folder:
                    logger.info(
                        f"[GoogleDrive _ensure_root_permissions_are_correct()] user {gdrive_user} should "
                        "have access to the root google drive folder but does not, attempting to grant "
                        "them access now."
                    )
                    self.add_users_gdrive([gdrive_user])

    def _validate_individual_file_and_folder_ownership_and_permissions(self, google_drive_perms, parent_id=None,
                                                                       files_to_email_owner_about=None):
        """Goes through each single file and folder under "CSSS" root folder and checking each file/folder to make sure
         that either it has the proper permission sets or is duplicated or its owner notified that
         they need to correct who the owner of the file is so that its permissions can be corrected

         Keyword Arguments
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
                    pageToken=next_page_token,
                    fields='*',
                    pageSize=999,
                    q=f"'{parent_id[len(parent_id) - 1]}' in parents AND trashed = false"
                ).execute()
            except Exception as e:
                logger.error(
                    "[GoogleDrive _validate_individual_file_and_folder_ownership_and_permissions()] "
                    f"unable to get the list of files under folder with id {parent_id[len(parent_id) - 1]}"
                    f" due to following error\n.{e}"
                )
                return
            for file in response['files']:
                self._validate_permissions_for_file(google_drive_perms, parent_id, file)
                files_to_email_owner_about = self._validate_owner_for_file(
                    google_drive_perms, parent_id, files_to_email_owner_about, file
                )
            if 'nextPageToken' not in response:
                # no more files to look at under this folder so need to go back up the recursive stack
                return files_to_email_owner_about
            next_page_token = response['nextPageToken']

    def _validate_permissions_for_file(self, google_drive_perms, parent_id, file):
        """
        Ensure that there are not permissions for files that should not exist

        Keyword Argument
         google_drive_perms -- a dict that list all the permissions that currently need to be set
         parent_id -- the folder that needs to have its contents searched
         file -- the info for the file that needs to have its permissions validated

        """
        # first going through all the permissions for the file to ensure
        # that they are correct according to the
        # google drive perms dictionary
        logger.info(
            "[GoogleDrive _validate_permissions_for_file()] ensuring that the permissions for file "
            f"{file['name']} are correct"
        )
        for permission in file['permissions']:
            if permission['id'] == 'anyoneWithLink':
                # check files that are link-share enabled
                if 'anyoneWithLink' not in google_drive_perms.keys():
                    # there are no link-shares enabled at this time
                    logger.info(
                        "[GoogleDrive _validate_permissions_for_file()] removing public "
                        f"link for file with id {file['id']} and name {file['name']}"
                    )
                    self.remove_public_link_gdrive(file['id'])
                else:
                    if set(google_drive_perms['anyoneWithLink']).intersection(
                            parent_id + [file['id']]) == 0:
                        # check to see if this particular file has not been link-share enabled or
                        # one of this particular file's parent folders have also not been link-share enabled
                        logger.info(
                            "[GoogleDrive _validate_permissions_for_file()] removing public "
                            f"link for file with id {file['id']} and name {file['name']}"
                        )
                        self.remove_public_link_gdrive(file['id'])
            elif 'emailAddress' in permission:
                # checking permissions that are email-shared
                email_address = permission['emailAddress'].lower()
                if email_address not in google_drive_perms.keys():
                    # this email is not supposed to have access to any of the CSSS Google Drive Resources
                    logger.info(
                        "[GoogleDrive _validate_permissions_for_file()] remove "
                        f"{email_address}'s access to file {file['name']}"
                    )
                    self.remove_users_gdrive(email_address, file['id'])
                else:
                    if set(google_drive_perms[email_address]).intersection(
                            parent_id + [file['id']]) == 0:
                        # checks to see if this email is supposed to have access to either this file or
                        # one of its parent folders
                        logger.info(
                            "[GoogleDrive _validate_permissions_for_file()] remove "
                            f"{email_address}'s access to file {file['name']}"
                        )
                        self.remove_users_gdrive(email_address, file['id'])

    def _validate_owner_for_file(self, google_drive_perms, parent_id, files_to_email_owner_about, file):
        """
        Ensure that the permissions for the given file is sfucsss@gmail.com

        Keyword Argument
        google_drive_perms -- a dict that list all the permissions that currently need to be set
        parent_id -- the folder that needs to have its contents searched
        files_to_email_owner_about -- a dictionary of the files whose owners need to be informed
            that their permission needs to be updated
        file -- the info for the file that needs to have its permissions validated

        Return
        folder_to_change -- the current dictionary of the folders whose ownership needs to be changed
        """
        valid_ownership_for_file = self._owner_of_folder_is_correct(file)
        logger.debug(
            "[GoogleDrive _validate_owner_for_file()] file/folder "
            f"{file['name']} of type {file['mimeType']} with owner {file['owners'][0]['emailAddress'].lower()} "
            f"will {'not ' if valid_ownership_for_file else ''}have its owner be alerted."
        )
        if not valid_ownership_for_file:
            logger.info(
                "[GoogleDrive _validate_owner_for_file()] file/folder "
                f"{file['name']} of type {file['mimeType']} with owner {file['owners'][0]['emailAddress'].lower()} "
                f"will have its owner be alerted."
            )
            if self._determine_if_file_info_belongs_to_gdrive_folder(file) or self._file_is_gdrive_form(file):
                file_name = file['name']
                logger.info(
                    f"[GoogleDrive _validate_owner_for_file()] google drive file {file_name} "
                    "determined to be a folder or form"
                )
                for owner in file['owners']:
                    owner_email = owner['emailAddress'].lower()
                    link = file['webViewLink']
                    logger.info(
                        f"[GoogleDrive _validate_owner_for_file()] adding {owner_email} "
                        f"to the list of people who need to be alerted about changing "
                        f"ownership for folder or form {file_name}"
                    )
                    if owner_email in files_to_email_owner_about:
                        files_to_email_owner_about[owner_email]['file_infos'].append(
                            {
                                'file_name': file_name,
                                'file_link': link
                            }
                        )
                    else:
                        files_to_email_owner_about[owner_email] = {
                            'full_name': owner['displayName'],
                            'file_infos': [{
                                'file_name': file_name,
                                'file_link': link
                            }]
                        }
            elif self._file_is_gdrive_file(file):
                logger.info(
                    "[GoogleDrive _validate_owner_for_file()] file "
                    f"{file['name']} determined to be a regular google drive file"
                )
                self._alert_user_to_change_owner(file)
            else:
                logger.info(
                    "[GoogleDrive _validate_owner_for_file()] file "
                    f"{file['name']} determined to probably be an uploaded file"
                )
                if self._duplicate_file(file):
                    self._alert_user_to_delete_file(file)
        if self._determine_if_file_info_belongs_to_gdrive_folder(file):
            # this is a folder so we have to check to see if any of its files have a bad permission set
            return self._validate_individual_file_and_folder_ownership_and_permissions(
                google_drive_perms, parent_id=parent_id + [file['id']],
                files_to_email_owner_about=files_to_email_owner_about
            )
        return files_to_email_owner_about

    def _determine_if_file_id_belongs_to_gdrive_folder(self, file_id):
        """
        determines if the google drive file type is a folder

        Keyword Argument
        file_info -- the id for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is a folder
        """
        file_info = self.gdrive.files().get(
            fields='*',
            fileId=file_id
        ).execute()
        return self._determine_if_file_info_belongs_to_gdrive_folder(file_info)

    def _determine_if_file_info_belongs_to_gdrive_folder(self, file_info):
        """
        determines if the google drive file type is a folder

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is a folder
        """
        if 'mimeType' in file_info:
            logger.info(f"[GoogleDrive _determine_if_file_info_belongs_to_gdrive_folder()] "
                        f"parsing a file_info with a type of {file_info['mimeType']} ")
        else:
            logger.error("[GoogleDrive _determine_if_file_info_belongs_to_gdrive_folder()] "
                         f"unable to find a file type for file {file_info['name']}")
        return 'mimeType' in file_info and file_info['mimeType'] == 'application/vnd.google-apps.folder'

    def _owner_of_folder_is_correct(self, file_info):
        """
        determines if the owner of the google drive folder is correct

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the folder is owned by sfucsss or not
        """
        file_ownership = 'ownedByMe' in file_info and file_info['ownedByMe']
        if 'ownedByMe' in file_info:
            logger.info(f"[GoogleDrive _owner_of_folder_is_correct()] "
                        f"file is {'' if file_ownership else 'not '}owned by sfucsss@gmail.com")
        else:
            logger.error("[GoogleDrive _owner_of_folder_is_correct()] "
                         f"unable to find key 'ownedByMe' for file {file_info['name']}")
        return file_ownership

    def _file_is_gdrive_file(self, file_info):
        """
        determine if the file is a goggle-app type that can be commented on

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is of google-app type that can be commented on
        """
        file_type = 'mimeType' in file_info and 'google-apps' in file_info['mimeType'] and \
                    file_info['mimeType'] != "application/vnd.google-apps.form"
        if 'mimeType' in file_info:
            logger.info(f"[GoogleDrive _file_is_gdrive_file()] file type for file {file_info['name']} "
                        f"is {file_info['mimeType']}")
        else:
            logger.error("[GoogleDrive _file_is_gdrive_file()] "
                         f"unable to find key 'mimeType' for file {file_info['name']}")
        return file_type

    def _file_is_gdrive_form(self, file_info):
        """
        determine if the file is a goggle form

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is a google form
        """
        file_type = 'mimeType' in file_info and file_info['mimeType'] == "application/vnd.google-apps.form"
        if 'mimeType' in file_info:
            logger.info(f"[GoogleDrive _file_is_gdrive_file()] file type for file {file_info['name']} "
                        f"is {file_info['mimeType']}")
        else:
            logger.error("[GoogleDrive _file_is_gdrive_file()] "
                         f"unable to find key 'mimeType' for file {file_info['name']}")
        return file_type

    def _alert_user_to_change_owner(self, file_info):
        """
        adds a comment to the file to alert the owner that they need to change the owner of the google drive file

        Keyword Argument
        file_info -- the file that needs to have the comment added to it
        """
        try:
            body = {'content': (
                "Please change owner of this file to sfucsss@gmail.com.\nInstructions for doing so can be found"
                " here: https://github.com/CSSS/managingCSSSResources"
            )}
            logger.info(f"[GoogleDrive _alert_user_to_change_owner()] attempting to add a comment added "
                        f"to file {file_info['name']}")
            response = self.gdrive.comments().create(fileId=file_info['id'], fields="*", body=body).execute()
            if response['content'] == body['content']:
                logger.info(f"[GoogleDrive _alert_user_to_change_owner()] comment added to file {file_info['name']}")
            else:
                logger.error(f"[GoogleDrive _alert_user_to_change_owner()] unable to add comment"
                             f" to file {file_info['name']}")
        except Exception as e:
            logger.error(
                f"[GoogleDrive _alert_user_to_change_owner()] unable to add comment to file {file_info['name']} "
                f"of type {file_info['mimeType']} due to following error.\n{e}"
            )

    def _duplicate_file(self, file_info):
        """
        Duplicates a non-google native document and renames the original to indicate it should no longer
        be used

        Keyword Arguments:
        file_info -- the file_info for the file that needs to be duplicated

        Return
        Bool -- true or false to indicate if the file was successfully duplicated
        """
        try:
            if file_info['name'] != 'duplicated__do_not_use':
                logger.info(
                    f"[GoogleDrive _duplicate_file()] "
                    f"attempting to duplicate file {file_info['name']} with id {file_info['id']}")
                self.gdrive.files().copy(
                    fileId=file_info['id'],
                    fields='*',
                    body={'name': file_info['name']}
                ).execute()
                logger.info(
                    f"[GoogleDrive _duplicate_file()] "
                    f"file {file_info['name']} with id {file_info['id']} successfully duplicated")
                body = {'name': 'duplicated__do_not_use'}
                logger.info(
                    f"[GoogleDrive _duplicate_file()]  attempting to set the body "
                    f"for file {file_info['name']} with id {file_info['id']} to {body}")
                self.gdrive.files().update(fileId=file_info['id'], body=body).execute()
                logger.info(
                    f"[GoogleDrive _duplicate_file()] "
                    f"file {file_info['name']} with id {file_info['id']}'s body successfully updated")
            return True
        except Exception as e:
            logger.error(
                f"[GoogleDrive _duplicate_file()] "
                f"unable to duplicate the file due to following error.\n{e}"
            )
            return False

    def _alert_user_to_delete_file(self, file_info):
        """
        alert the owner of a file via a comment that its needs to be deleted

        Keyword Argument
        file_info -- the info for the file that needs to be deleted
        """
        try:
            body = {'content': (
                "Please delete this file as it has been duplicated and is no longer the latest version of this file"
            )}
            response = self.gdrive.comments().create(fileId=file_info['id'], fields="*", body=body).execute()
            if response['content'] == body['content']:
                logger.info(f"[GoogleDrive _alert_user_to_delete_file()] comment added to file {file_info['name']}")
            else:
                logger.error(
                    f"[GoogleDrive _alert_user_to_delete_file()] unable to add comment to file {file_info['name']}")
        except Exception as e:
            logger.error(
                f"[GoogleDrive _alert_user_to_delete_file()] unable to add comment to file {file_info['name']} "
                f"of type {file_info['mimeType']} due to following error.\n{e}"
            )

    def _send_email_notifications_for_files_with_incorrect_ownership(self, files_to_email_owner_about):
        """
        will email all the relevant owners of the folders that they are owners of that need to have
        their ownership changed

        Keyword Argument
        files_to_email_owner_about -- a dictionary that contains a list of all the emails and their corresponding
            files that they need to be made aware of that have to have their ownership changed
        """
        gmail_credentials = GoogleMailAccountCredentials.objects.all().filter(username="sfucsss@gmail.com")
        if len(gmail_credentials) == 0:
            logger.error("[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] "
                         "Could not find any credentials for the gmail "
                         "sfucsss@gmail.com account in order to send notification email")
        sfu_csss_credentials = gmail_credentials[0]
        logger.info("[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] attempting"
                    " to setup connection to gmail server")
        gmail = Gmail(sfu_csss_credentials.username, sfu_csss_credentials.password)
        subject = "SFU CSSS Google Drive Folder ownership change"
        body_template = (
            "Please change owner of the following folders and forms to sfucsss@gmail.com.\n"
            "Instructions for doing so can be "
            "found  here: https://github.com/CSSS/managingCSSSResources\n\nFolders whose ownership needs "
            "to be changed:\n"
        )
        for to_email in files_to_email_owner_about:
            body = body_template + "".join(
                [
                    f"{file['file_name']} : {file['file_link']}\n" for file in
                    files_to_email_owner_about[to_email]['file_infos']
                ]
            )
            files_names = [file['file_name'] for file in files_to_email_owner_about[to_email]['file_infos']]
            to_name = files_to_email_owner_about[to_email]['full_name']
            logger.info("[GoogleDrive _send_email_notifications_for_files_with_incorrect_ownership()] attempting to "
                        f"send email to {to_email} about files {files_names}")
            gmail.send_email(subject, body, to_email, to_name)
        gmail.close_connection()
