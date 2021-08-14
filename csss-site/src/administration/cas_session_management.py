import json
import logging

import requests
import xmltodict
from django.conf import settings
from django.http import HttpResponseRedirect

from administration.Constants import CURRENT_WEBMASTER_OR_DOA, OFFICER_IN_PAST_5_TERMS, CURRENT_ELECTION_OFFICER, \
    CURRENT_SYS_ADMIN, CURRENT_SYS_ADMIN_OR_WEBMASTER, USER_SFUID
from resource_management.views.get_officer_list import get_list_of_officer_details_from_past_specified_terms

logger = logging.getLogger('csss_site')


def cas_login(request):
    ticket = request.GET.get("ticket", None)
    if ticket is not None:
        request_path = f"http://{settings.HOST_ADDRESS}"
        if settings.PORT is not None:
            request_path += f":{settings.PORT}"
        request_path += f"{request.path}"
        endpoint = f"https://cas.sfu.ca/cas/serviceValidate?service={request_path}&ticket={ticket}"
        response = requests.get(endpoint)
        try:
            sfu_cas_response = json.loads(json.dumps(xmltodict.parse(response.text)))
            sfuid = sfu_cas_response['cas:serviceResponse']['cas:authenticationSuccess']['cas:user']

            current_webmaster_or_doa_sfuid = get_list_of_officer_details_from_past_specified_terms(
                relevant_previous_terms=0, position_names=["Webmaster", "Director of Archives"], filter_by_sfuid=True
            )

            current_sys_admin_sfuid = get_list_of_officer_details_from_past_specified_terms(
                relevant_previous_terms=0, position_names=["Systems Administrator"], filter_by_sfuid=True
            )

            current_sys_admin_or_webmaster_sfuid = get_list_of_officer_details_from_past_specified_terms(
                relevant_previous_terms=0, position_names=["Webmaster", "Systems Administrator"], filter_by_sfuid=True
            )

            sfuid_for_officer_in_past_5_terms = get_list_of_officer_details_from_past_specified_terms(
                filter_by_sfuid=True
            )

            current_election_officer_sfuid = get_list_of_officer_details_from_past_specified_terms(
                relevant_previous_terms=0, position_names=["General Election Officer", "By-Election Officer"],
                filter_by_sfuid=True
            )
            request.session[USER_SFUID] = sfuid
            request.session[CURRENT_WEBMASTER_OR_DOA] = sfuid in current_webmaster_or_doa_sfuid
            request.session[CURRENT_SYS_ADMIN] = sfuid in current_sys_admin_sfuid
            request.session[CURRENT_SYS_ADMIN_OR_WEBMASTER] = sfuid in current_sys_admin_or_webmaster_sfuid
            request.session[OFFICER_IN_PAST_5_TERMS] = sfuid in sfuid_for_officer_in_past_5_terms
            request.session[CURRENT_ELECTION_OFFICER] = sfuid in current_election_officer_sfuid
        except Exception as e:
            logger.info(
                f"[elections/election_page.py detect_login()] Unable to get SFU ID due to following error: {e}"
            )


def cas_logout(request):
    del request.session[USER_SFUID]
    del request.session[CURRENT_WEBMASTER_OR_DOA]
    del request.session[CURRENT_SYS_ADMIN]
    del request.session[CURRENT_SYS_ADMIN_OR_WEBMASTER]
    del request.session[OFFICER_IN_PAST_5_TERMS]
    del request.session[CURRENT_ELECTION_OFFICER]
    return HttpResponseRedirect("https://cas.sfu.ca/cas/logout")
