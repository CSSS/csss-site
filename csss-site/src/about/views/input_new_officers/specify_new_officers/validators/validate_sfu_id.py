import json

import requests
from django.conf import settings


def validate_sfu_id(sfu_computing_id):
    """
    Ensures that the given sfu id for a New_Officer is correct

    Keyword Argument
    sfu_computing_id -- the sfu id of the New_Officer to validate

    Return
    bool -- indicator of whether the validation was successful
    error_message -- whatever error message there was as a result of the validation, or None
    """
    if settings.SFU_ENDPOINT_TOKEN is None:
        return True, None
    resp = requests.get(
        f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/amaint/namespace.json?"
        f"id={sfu_computing_id}&art={settings.SFU_ENDPOINT_TOKEN}"
    )
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}'"
    if not (json.loads(resp.text)['type'] == "username" and json.loads(resp.text)['username'] == sfu_computing_id):
        return False, f"{sfu_computing_id} is not a valid sfu_computing_id"
    return True, None
