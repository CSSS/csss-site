import requests
from django.conf import settings


def validate_sfu_id(cls, sfu_computing_id):
    if settings.SFU_ENDPOINT_TOKEN is None:
        return True
    resp = requests.get(
        f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/amaint/namespace.json?"
        f"id={sfu_computing_id}&art={settings.SFU_ENDPOINT_TOKEN}"
    )
    if resp.status_code != 200:
        return False, f"Encountered error message of '{resp.reason}'"
    return True, None
