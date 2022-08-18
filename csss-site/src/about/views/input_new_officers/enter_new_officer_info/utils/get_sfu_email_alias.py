import json

import requests
from django.conf import settings


def get_sfu_email_alias(sfu_computing_id):
    """
    Ensures that the given sfu id for a New_Officer is correct

    Keyword Argument
    sfu_computing_id -- the sfu id of the New_Officer to validate

    Return
    bool -- indicator of whether the validation was successful
    error_message -- whatever error message there was as a result of the validation, or None
    email_alias -- the user's email alias
    """
    if settings.SFU_ENDPOINT_TOKEN is None:
        return True, None, None
    resp = requests.get(
        f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/datastore2/global/accountInfo.js?"
        f"username={sfu_computing_id}&art={settings.SFU_ENDPOINT_TOKEN}"
    )
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}'", None
    if (
        'aliases' not in json.loads(resp.text) or
        type(json.loads(resp.text)['aliases']) is not list or
            len(json.loads(resp.text)['aliases']) <= 0):
        return False, f"Could not detect email alias for {sfu_computing_id}", None
    return True, None, json.loads(resp.text)['aliases'][0]
