import json
from time import sleep

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
                f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/amaint/namespace.json?"
                f"id={sfu_computing_id}&art={settings.SFU_ENDPOINT_TOKEN}"
            )
        except Exception as e:
            if len(e.args) > 0 and len(e.args[0].args) > 1 and len(e.args[0].args[1].args) > 1:
                connection_reset = e.args[0].args[1].args[1] == 'Connection reset by peer'
    if number_of_tries == 5:
        return False, f"Unable to validate the SFU ID {sfu_computing_id} as connection keeps getting reset"
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}' when validating SFU ID {sfu_computing_id}"
    if not (json.loads(resp.text)['type'] == "username" and json.loads(resp.text)['username'] == sfu_computing_id):
        return False, f"{sfu_computing_id} is not a valid sfu_computing_id"
    return True, None
