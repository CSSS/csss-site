from csss.setup_logger import Loggers
from resource_management.views.resource_apis.gdrive.gdrive_api import GoogleDrive


def grant_google_drive_access(grant_gdrive_access, gmail):
    """
    Grant the specific gmail access to the SFU CSSS Google drive

    Keyword Argument
    grant_gdrive_access -- indicates if the user is supposed to be given access to the SFU CSSS Google Drive
    gmail -- the gmail that may be given access to the SFU CSSS Google Drive

    Return
    bool -- True or false depending on if there was an issue with talking to the google drive API
    error_message -- the message received alongside the error
    """
    logger = Loggers.get_logger()
    if grant_gdrive_access and gmail is not None:
        gdrive_api = GoogleDrive()
        if gdrive_api.connection_successful is False:
            logger.info("[about/grant_google_drive_access.py grant_google_drive_access()]"
                        f" {gdrive_api.error_message}")
            return False, gdrive_api.error_message
        success, file_name, error_message = gdrive_api.add_users_gdrive([gmail])
        if not success:
            return success, error_message
    return True, None
