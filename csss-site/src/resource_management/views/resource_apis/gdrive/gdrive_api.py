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
                return False, None, e

            file_name = response['name']
            for user in users:
                email_message = (
                    f"Hello {user},"
                    "You have been granted acces to a subfolder in the CSSS Google Drive. "
                    "Please be careful when deleting as you have \"master\" access, as do all the officers."
                    "Furthermore, when creating a file on the CSSS Google Drive, please "
                    "try to transfer ownerships of any files you create to \"sfucsss@gmail.com\" account "
                    "as this makes it easier for me to remove your access when it's time to revoke it."
                    "You can figure out how to do that with these instructions: "
                    "https://github.com/CSSS/managingCSSSResources/tree/master/google_drive"
                    "-Your Sys Admin"
                )
                body = {}
                body['role'] = 'writer'
                body['type'] = 'user'
                body['emailAddress'] = user.lower()
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
                    return False, None, e
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
            body = {}
            body['role'] = 'writer'
            body['type'] = 'anyone'
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

    def ensure_root_permissions_are_correct(self, google_drive_perms):
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
                    "[GoogleDrive ensure_root_permissions_are_correct()] unable to get all the files "
                    f"under root due to following error.\n {e}")
                return False
            # first doing a check for the permissions to the root folder "CSSS"
            # once the new permissions have gone through, will check each individual file to make sure
            # there is nothing else that has access that should not have it.
            for permission in response['permissions']:
                if permission['emailAddress'].lower() in google_drive_perms:
                    if self.root_file_id not in google_drive_perms[permission['emailAddress'].lower()]:
                        # it has found an individual who has access to the root folder even though their key/value
                        # indicates that they should actually have access to another folder/file
                        logger.info(
                            "[GoogleDrive ensure_root_permissions_are_correct()] will attempt to remove "
                            f" {permission['emailAddress'].lower()}'s permission to the root folder"
                        )
                        self.remove_users_gdrive([permission['emailAddress'].lower()], self.root_file_id)
                else:
                    # have found an individual who should not have access to anything at all.
                    self.remove_users_gdrive([permission['emailAddress'].lower()], self.root_file_id)

            # once the function tries to set the permissions correctly at the top-level, it will then wait 10 second
            # to give time for the above changes to propagate through before it does a call to
            # ensure_permissions_are_correct to deal with cases where subfiles/folders are now owned
            # by sfucsss@gmail.com which prevents removing the owner of that file from the drive
            time.sleep(10)
            folders_to_change = self.ensure_permissions_are_correct(google_drive_perms, [self.root_file_id], {})
            self.send_email_notifications_for_folder_with_incorrect_ownership(folders_to_change)

    def ensure_permissions_are_correct(self, google_drive_perms, parent_id, folders_to_change):
        """Goes through each single file and folder under "CSSS" root folder and checking each file/folder to make sure
         that either it has the proper permission sets or is duplicated or its owner notified that
         they need to correct who the owner of the file is so that its permissions can be corrected

         Keyword Arguments:
         google_drive_perms -- a dict that list all the permissions that currently need to be set
         parent_id -- the folder folder that needs to have its contents searched
        """
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
                    "[GoogleDrive ensure_permissions_are_correct()] unable to get the list of files "
                    f"under folder with id {parent_id[len(parent_id) - 1]} due to following error\n.{e}"
                )
                return
            for file in response['files']:
                logger.info(
                    "[GoogleDrive ensure_permissions_are_correct()] ensuring that the permissions for file "
                    f"{file['name']} are correct"
                )
                # first going through all the permissions for the file to ensure
                # that they are correct according to the
                # google drive perms dictionary
                for permission in file['permissions']:
                    if permission['id'] == 'anyoneWithLink':
                        # check files that are link-share enabled
                        if 'anyoneWithLink' not in google_drive_perms.keys():
                            # there are no link-shares enabled at this time
                            logger.info(
                                "[GoogleDrive ensure_permissions_are_correct()] removing public "
                                f"link for file with id {file['id']} and name {file['name']}"
                            )
                            self.remove_public_link_gdrive(file['id'])
                        else:
                            if set(google_drive_perms['anyoneWithLink']).intersection(
                                    parent_id + [file['id']]) == 0:
                                # check to see if this particular file has not been link-share enabled or
                                # one of this particular file's parent folders have also not been link-share enabled
                                logger.info(
                                    "[GoogleDrive ensure_permissions_are_correct()] removing public "
                                    f"link for file with id {file['id']} and name {file['name']}"
                                )
                                self.remove_public_link_gdrive(file['id'])
                    elif 'emailAddress' in permission:
                        # checking permissions that are email-shared
                        email_address = permission['emailAddress'].lower()
                        if email_address not in google_drive_perms.keys():
                            # this email is not supposed to have access to any of the CSSS Google Drive Resources
                            logger.info(
                                "[GoogleDrive ensure_permissions_are_correct()] remove "
                                f"{email_address}'s access to file {file['name']}"
                            )
                            self.remove_users_gdrive(email_address, file['id'])
                        else:
                            if set(google_drive_perms[email_address]).intersection(
                                    parent_id + [file['id']]) == 0:
                                # checks to see if this email is supposed to have access to either this file or
                                # one of its parent folders
                                logger.info(
                                    "[GoogleDrive ensure_permissions_are_correct()] remove "
                                    f"{email_address}'s access to file {file['name']}"
                                )
                                self.remove_users_gdrive(email_address, file['id'])
                if self.file_is_gdrive_folder(file):
                    logger.info(
                        "[GoogleDrive ensure_permissions_are_correct()] file "
                        f"{file['name']} determined to be a folder"
                    )
                    success, folder_name = self.owner_of_folder_is_correct(file)
                    if not success:
                        logger.info(
                            "[GoogleDrive ensure_permissions_are_correct()] owner for folder "
                            f"{file['name']} is not sfucsss"
                        )
                        for owner in file['owners']:
                            owner_email = owner['emailAddress'].lower()
                            link = file['webViewLink']
                            logger.info(
                                f"[GoogleDrive ensure_permissions_are_correct()] adding {owner_email} "
                                f"to the list of people who need to be alerted about changing "
                                f"ownership for folder {file['name']}"
                            )
                            if owner_email in folders_to_change:
                                folders_to_change[owner_email]['folder_infos'].append(
                                    {
                                        'folder_name': folder_name,
                                        'folder_link': link
                                    }
                                )
                            else:
                                folders_to_change[owner_email] = {
                                    'full_name': owner['displayName'],
                                    'folder_infos': [{
                                        'folder_name': folder_name,
                                        'folder_link': link
                                    }]
                                }
                    # this is a folder so we have to check to see if any of its files have a bad permission set
                    folders_to_change = self.ensure_permissions_are_correct(
                        google_drive_perms, parent_id + [file['id']], folders_to_change
                    )
                elif self.file_is_gdrive_file(file):
                    logger.info(
                        "[GoogleDrive ensure_permissions_are_correct()] file "
                        f"{file['name']} determined to be a regular google drive file"
                    )
                    self.alert_user_to_change_owner(file)
                else:
                    logger.info(
                        "[GoogleDrive ensure_permissions_are_correct()] file "
                        f"{file['name']} determined to probably be an uploaded file"
                    )
                    if not self.file_is_owned_by_sfucsss(file):
                        logger.info(
                            "[GoogleDrive ensure_permissions_are_correct()] file "
                            f"{file['name']} does not appear to be owned by sfucsss@gmail.com"
                        )
                        self.duplicate_file(file)
                        self.alert_user_to_delete_file(file)
            if 'nextPageToken' not in response:
                # no more files to look at under this folder so need to go back up the recursive stack
                return folders_to_change
            next_page_token = response['nextPageToken']

    def file_is_gdrive_folder(self, file_info):
        """
        determines if the google drive file type is a folder

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is a folder
        """
        return file_info['mimeType'] == 'application/vnd.google-apps.folder'

    def owner_of_folder_is_correct(self, file_info):
        """
        determines if the owner of the google drive folder is correct

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the folder is owned by sfucsss or not
        name -- the name of the folder, if it is not owned by sfucsss. otherwise None
        """
        if file_info['ownedByMe']:
            return True, None
        else:
            return False, file_info['name']

    def file_is_gdrive_file(self, file_info):
        """
        determine if the file is a goggle-app type

        Keyword Argument
        file_info -- the info for the file whose type needs to be checked

        Return
        Bool -- true or false to indicate if the file is of google-app type
        """
        return 'google-apps' in file_info['mimeType']

    def alert_user_to_change_owner(self, file_info):
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
            logger.info(f"[GoogleDrive alert_user_to_change_owner()] attempting to add a comment added "
                        f"to file {file_info['name']}")
            self.gdrive.comments().create(fileId=file_info['id'], fields="*", body=body).execute()
            logger.info(f"[GoogleDrive alert_user_to_change_owner()] comment added to file {file_info['name']}")
        except Exception as e:
            logger.error(
                f"[GoogleDrive alert_user_to_change_owner()] unable to add comment to file {file_info['name']} "
                f"of type {file_info['mimeType']} due to following error.\n{e}"
            )

    def file_is_owned_by_sfucsss(self, file_info):
        """
        indicate if the file is owned by the sfucsss account

        Keyword Argument
        file_info -- the info for the file that needs to have its ownership checked

        Return
        Bool -- true or false to indicate if it is owned by sfucsss gmail account
        """
        return file_info['ownedByMe']

    def duplicate_file(self, file_info):
        """
        Duplicates a non-google native document and renames the original to indicate it should no longer
        be used

        Keyword Arguments:
        file_info -- the file_info for the file that needs to be duplicated
        """
        try:
            if file_info['name'] != 'duplicated__do_not_use':
                logger.info(
                    f"[GoogleDrive duplicate_file()] "
                    f"attempting to duplicate file {file_info['name']} with id {file_info['id']}")
                duplicate_file_name = {
                    'name': file_info['name']
                }
                self.gdrive.files().copy(fileId=file_info['id'], fields='*', body=duplicate_file_name).execute()
                logger.info(
                    f"[GoogleDrive duplicate_file()] "
                    f"file {file_info['id']} successfully duplicated")
                body = {'name': 'duplicated__do_not_use'}
                logger.info(
                    f"[GoogleDrive duplicate_file()]  attempting to set the body "
                    f"for file {file_info['id']} to {body}")
                self.gdrive.files().update(fileId=file_info['id'], body=body).execute()
                logger.info(
                    f"[GoogleDrive duplicate_file()] "
                    f"file {file_info['id']}'s body successfully updated")
        except Exception as e:
            logger.error(
                f"[GoogleDrive duplicate_file()] "
                f"unable to duplicate the file due to following error.\n{e}"
            )

    def alert_user_to_delete_file(self, file_info):
        """
        alert the owner of a file via a comment that its needs to be deleted

        Keyword Argument
        file_info -- the info for the file that needs to be deleted
        """
        try:
            body = {'content': (
                "Please delete this file as it has been duplicated and is no longer the latest version of this file"
            )}
            self.gdrive.comments().create(fileId=file_info['id'], fields="*", body=body).execute()
            logger.info(f"[GoogleDrive alert_user_to_delete_file()] comment added to file {file_info['name']}")
        except Exception as e:
            logger.error(
                f"[GoogleDrive alert_user_to_delete_file()] unable to add comment to file {file_info['name']} "
                f"of type {file_info['mimeType']} due to following error.\n{e}"
            )

    def send_email_notifications_for_folder_with_incorrect_ownership(self, folders_to_change):
        """
        will email all the relevant owners of the folders that they are owners of that need to have
        their ownership changed

        Keyword Argument
        folders_to_change -- a dictionary that contains a list of all the emails and their corresponding
            folders that they need to be made aware of that have to have their ownership changed
        """
        gmail_credentials = GoogleMailAccountCredentials.objects.all().filter(username="sfucsss@gmail.com")
        if len(gmail_credentials) == 0:
            logger.error("[GoogleDrive send_email_notifications_for_folder_with_incorrect_ownership()] "
                         "Could not find any credentials for the gmail "
                         "sfucsss@gmail.com account in order to send notification email")
        sfu_csss_credentials = gmail_credentials[0]
        logger.info("[GoogleDrive send_email_notifications_for_folder_with_incorrect_ownership()] attempting"
                    " to setup connection to gmail server")
        gmail = Gmail(sfu_csss_credentials.username, sfu_csss_credentials.password)
        subject = "SFU CSSS Google Drive Folder ownership change"
        body_template = (
            "Please change owner of the following folders to sfucsss@gmail.com.\n"
            "Instructions for doing so can be "
            "found  here: https://github.com/CSSS/managingCSSSResources\n\nFolders whose ownership needs "
            "to be changed:\n"
        )
        for to_email in folders_to_change:
            body = body_template + "".join(
                [
                    f"{folder['folder_name']} : {folder['folder_link']}\n" for folder in
                    folders_to_change[to_email]['folder_infos']
                ]
            )
            to_name = folders_to_change[to_email]['full_name']
            logger.info("[GoogleDrive send_email_notifications_for_folder_with_incorrect_ownership()] attempting to "
                        f"send email to {to_email}")
            gmail.send_email(subject, body, to_email, to_name)
        gmail.close_connection()
