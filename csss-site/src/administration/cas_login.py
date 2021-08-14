import json
import logging

import requests
import xmltodict
from django.conf import settings

from resource_management.views.get_officer_list import get_list_of_officer_details_from_past_specified_terms

logger = logging.getLogger('csss_site')


def interpret_sfu_cas_response(request):
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

            # only do this is the SFUID belong to user who was an officer in past 5 terms
            sfuid = sfu_cas_response['cas:serviceResponse']['cas:authenticationSuccess']['cas:user']
            """
            webmaster or DoA:
            creating officer creation links -- webmaster or DoA
            upload officer lists -- Webmaster or DoA
            update position mappings -- webmaster or DoA


            Sys Admin
            update github mapping
            github permission management


            Webmaster or Sys Admin
            accessing /admin

            officer in past 5 years
            current and past officer details
            google drive permission management

            Current Election Officer
            CRU elections

            how to determine whether to display login link or user's username -- if SFUID in cookies    



            'authenticated': request.user.is_authenticated,
            creating officer creation links
            uploading officer lists
            updating positions and github mapping
            google drive and github permission management
            how to determine whether to display login link or user's username
            current and past officer details

            'authenticated_officer': ('officer' in groups),
            current and past officer details

            ELECTION_MANAGEMENT_GROUP_NAME: (ELECTION_MANAGEMENT_GROUP_NAME in groups), //election_management && election_management_permission
            create and modify elections

            'staff': request.user.is_staff,
            creating officer creation links
            uploading officer lists
            updating positions and github mapping
            current and past officer details
            google drive and github permission management
            how to determine whether to display login link or user's username

            """
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
            request.COOKIES["sfuid"] = sfuid
            request.COOKIES["current_webmaster_or_doa"] = sfuid in current_webmaster_or_doa_sfuid
            request.COOKIES["current_sys_admin"] = sfuid in current_sys_admin_sfuid
            request.COOKIES["current_sys_admin_or_webmaster"] = sfuid in current_sys_admin_or_webmaster_sfuid
            request.COOKIES["officer_in_past_5_terms"] = sfuid in sfuid_for_officer_in_past_5_terms
            request.COOKIES["current_election_officer"] = sfuid in current_election_officer_sfuid
        except Exception as e:
            logger.info(f"[elections/election_page.py detect_login()] Unable to get SFU ID due to following error: {e}")

