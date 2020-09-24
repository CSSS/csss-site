import logging
import os
import pickle
import time

import googleapiclient
from django.conf import settings

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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
                    logger.info(f"[GoogleDrive __init__()] {self.error_message} ")
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
                    logger.info(
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
                                logger.info(
                                    "[GoogleDrive remove_users_gdrive()] encountered following error "
                                    f"with permission removed. \n {e}"
                                )
            except Exception as e:
                logger.info(
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
                logger.info("[GoogleDrive make_public_link_gdrive()] Please specify a valid file_id")
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
                logger.info(f"[GoogleDrive make_public_link_gdrive()] encountered the following error. \n {e}")
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
                logger.info(
                    "[GoogleDrive remove_public_link_gdrive()] experienced the following error when "
                    f"attempting to removing public link for file with id {file_id}.\n {e}"
                )

    def check_parent_folder(self, file_id, parent_folder):
        """
        Purpose: recursively gets the parent info of the parent until it is at the top
        this is being done in order to determine if subfile or subfolder exists in a file
        that has been shared with someone
        NOT BEING USED ANYMORE
        """
        if self.connection_successful:
            while True:
                response = self.gdrive.files().get(fileId=file_id, fields='*').execute()
                # logger.info(json.dumps(daResponse, indent=4, sort_keys=True))
                if response['id'] == parent_folder:
                    return True
                if 'parents' not in response:
                    return False
                file_id = response['parents'][0]
                # id, name and parent id

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
                logger.info(
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
            self.ensure_permissions_are_correct(google_drive_perms, [self.root_file_id])

    def ensure_permissions_are_correct(self, google_drive_perms, parent_id):
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
                logger.info(
                    "[GoogleDrive ensure_permissions_are_correct()] unable to get the list of files "
                    f"under folder with id {parent_id[len(parent_id) - 1]} due to following error\n.{e}"
                )
                return
            for file in response['files']:
                logger.info(
                    "[GoogleDrive ensure_permissions_are_correct()] attempting to "
                    f"fix file permissions for file {file['name']}"
                )
                self.ensure_correct_owner_for_file(file)
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
                            if set(google_drive_perms['anyoneWithLink']).intersection(parent_id + [file['id']]) == 0:
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
                            if set(google_drive_perms[email_address]).intersection(parent_id + [file['id']]) == 0:
                                # checks to see if this email is supposed to have access to either this file or
                                # one of its parent folders
                                logger.info(
                                    "[GoogleDrive ensure_permissions_are_correct()] remove "
                                    f"{email_address}'s access to file {file['name']}"
                                )
                                self.remove_users_gdrive(email_address, file['id'])
                if file['mimeType'] == "application/vnd.google-apps.folder":
                    # this is a folder so we have to check to see if any of its files have a bad permission set
                    self.ensure_permissions_are_correct(google_drive_perms, parent_id + [file['id']])
            if 'nextPageToken' not in response:
                # no more files to look at under this folder so need to go back up the recursive stack
                return
            next_page_token = response['nextPageToken']

    def ensure_correct_owner_for_file(self, file_info):
        """Checks what kind of a file has been passed and what needs to happen to ensure its owner is sfucsss@gmail.com

        Keyword Arguments:
        file_info -- the file_info for the file that needs to have its permissions checked
        """
        if 'google-apps' not in file_info['mimeType']:
            # any file that is not a google native document cannot have its owner changes,
            # it needs to be duplicated instead.
            if file_info['ownedByMe']:
                return True
            else:
                self.duplicate_file(file_info)
                return True
        else:
            # only the owner of a google native document can change its owner
            if not file_info['ownedByMe']:
                self.alert_user_to_change_owner(file_info)
                return False
            else:
                return True

    def duplicate_file(self, file_info):
        """Duplicates a non-google native document and removes the duplicate so that the version on the drive is owned
        by sfucsss@gmail.com

        Keyword Arguments:
        file_info -- the file_info for the file that needs to have its permissions checked
        """
        try:
            self.gdrive.files().copy(fileId=file_info['id'], fields='*').execute()

            body = {}
            body['name'] = 'duplicated_and_removed'
            try:
                self.gdrive.files().update(fileId=file_info['id'], body=body).execute()
            except Exception as e:
                logger.info(
                    f"[GoogleDrive duplicate_file()] counldnt update {file_info['name']} to "
                    f"\"duplicated_and_removed\" due to following error.\n{e}"
                )
                return

            # google drive api doesnt allow a function that "removes" a file from the sfucsss@gmail.com's
            # google drive.
            # it only allows a file that deletes it and deleting a file can only be done by the owner.
            # the only alternative seems to be to just remove all permissions from the file so that only the
            # original owner can see it.
            for permission in file_info['permissions']:
                if "emailAddress" in permission:
                    if permission['emailAddress'].lower() == "sfucsss@gmail.com":
                        # sfucsss@gmail.com's permissions is being saved to be removed later on as it needs to
                        # keep its access to the file in order to remove any remaining non-owner permissions
                        # that may exist.
                        sfucsss_permission_id = permission['id']
                    else:
                        try:
                            self.gdrive.permissions().delete(
                                fileId=file_info['id'],
                                permissionId=permission['id']
                            ).execute()
                            logger.info(
                                f"[GoogleDrive duplicate_file()] removed {permission['emailAddress'].lower()}'s "
                                f"access to {file_info['name']}"
                            )
                        except Exception as e:
                            logger.info(
                                "[GoogleDrive duplicate_file()] couldnt remove "
                                f"{permission['emailAddress'].lower()}'s access to {file_info['name']} "
                                f"due to following error.\n{e}"
                            )
                            return
            self.gdrive.permissions().delete(
                fileId=file_info['id'],
                permissionId=sfucsss_permission_id
            ).execute()
        except Exception as e:
            logger.info(
                f"[GoogleDrive duplicate_file()] unable to duplicate and remove file "
                f"from drive due to following error.\n{e}"
            )

    def alert_user_to_change_owner(self, file_info):
        try:
            body = {}
            body['content'] = (
                "Please change owner of this file to sfucsss@gmail.com.\nInstructions for doing so can be found"
                " here: https://github.com/CSSS/managingCSSSResources"
            )
            self.gdrive.comments().create(fileId=file_info['id'], fields="*", body=body).execute()
            logger.info(f"[GoogleDrive alert_user_to_change_owner()] comment added to file {file_info['name']}")
        except Exception as e:
            logger.info(
                f"[GoogleDrive alert_user_to_change_owner()] unable to add comment to file {file_info['name']} "
                f"due to following error.\n{e}"
            )
