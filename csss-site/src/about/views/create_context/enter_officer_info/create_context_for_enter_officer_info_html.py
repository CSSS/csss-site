import json

import requests
from django.conf import settings

from about.models import OfficerEmailListAndPositionMapping, Officer


def create_context_for_enter_officer_info_html(request, context, new_officer=None, new_officer_info=None):
    officer_emaillist_and_position_mapping = OfficerEmailListAndPositionMapping.objects.all().get(
        position_name=new_officer.position_name)
    context.update({
        "sfuid_email_alias_value": get_email_list(new_officer.sfu_computing_id),
        "sfuid_value": request.user.username

    })
    if new_officer_info is not None:
        context.update({
            "name_value": new_officer_info['name'],
            "sfuid_email_alias_value": new_officer_info['sfuid_email_alias'],
            "email_value": new_officer_info['email'],
            "gmail_value": new_officer_info['gmail'],
            "phone_number_value": new_officer_info['phone_number'],
            "github_username_value": new_officer_info['github_username'],
            "course1_value": new_officer_info['course1'],
            "course2_value": new_officer_info['course2'],
            "language1_value": new_officer_info['language1'],
            "language2_value": new_officer_info['language2'],
            "bio_value": new_officer_info['bio']
        })
    elif new_officer is not None:
        officer = Officer.objects.all().filter(
            sfuid=new_officer.sfu_computing_id
        ).order_by('-elected_term').first()
        if officer is not None:
            context.update({
                "name_value": officer.name,
                "sfuid_value": officer.sfuid,
                "sfuid_email_alias_value": officer.sfu_email_alias,
                "email_value": ",".join(officer.announcementemailaddress_set.all()),
                "gmail_value": officer.gmail,
                "phone_number_value": officer.phone_number,
                "github_username_value": officer.github_username,
                "course1_value": officer.course1,
                "course2_value": officer.course2,
                "language1_value": officer.language1,
                "language2_value": officer.language2,
                "bio_value": officer.bio
            })
    if new_officer is not None:
        context.update({
            "term_value": new_officer.term.term,
            "year_value": new_officer.term.year,
            "term_position_value": new_officer.position_name,
            "date_value": new_officer.start_date,
            "name_value": context["name_value"] if "name_value" in context else new_officer.full_name
        })


def get_email_list(sfuid):
    response = requests.get(
        f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/datastore2/global/"
        f"accountInfo.js?username={sfuid}&art={settings.SFU_ENDPOINT_TOKEN}"
    )
    if response.status_code == 200:
        return json.loads(response.text)['aliases'][0]
