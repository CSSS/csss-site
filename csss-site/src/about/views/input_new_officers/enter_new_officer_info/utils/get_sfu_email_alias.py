import json
from time import sleep

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
    connection_reset = False
    first_try = True
    number_of_tries = 0
    while (connection_reset or first_try) and number_of_tries < 5:
        if connection_reset:
            sleep(1)
        connection_reset = False
        first_try = False
        try:
            number_of_tries += 1
            resp = requests.get(
                f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/datastore2/global/accountInfo.js?"
                f"username={sfu_computing_id}&art={settings.SFU_ENDPOINT_TOKEN}"
            )
        except Exception as e:
            if len(e.args) > 0 and len(e.args[0].args) > 1 and len(e.args[0].args[1].args) > 1:
                connection_reset = e.args[0].args[1].args[1] == 'Connection reset by peer'
    if number_of_tries == 5:
        return False, f"Unable to get the email alias for SFU ID {sfu_computing_id} as connection keeps getting reset"
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}'", None
    if (
        'aliases' not in json.loads(resp.text) or
        type(json.loads(resp.text)['aliases']) is not list or
            len(json.loads(resp.text)['aliases']) <= 0):
        return False, f"Could not detect email alias for {sfu_computing_id}", None
    return True, None, json.loads(resp.text)['aliases'][0]
