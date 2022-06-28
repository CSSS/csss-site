import json

import requests
from django.conf import settings

from about.models import Officer


def create_context_for_enter_officer_info_html(
    request, context, new_officer_obj=None, new_officer_info_from_form=None, officer_from_previous_term=None):
    context.update({
        "term__html_name": "term",
        "year__html_name": "year",
        "position_name__html_name": "position_name",
        "date__html_name": "date",
        "position_index__html_name": "position_index",
        "sfu_email_list_address__html_name": "sfu_email_list_address",
        "officer_name__html_name": "officer_name",
        "officer_sfuid__html_name": "officer_sfuid",
        "officer_email_alias__html_name": "officer_email_alias",
        "officer_announcement_emails__html_name": "officer_announcement_emails",
        "officer_gmail__html_name": "officer_gmail",
        "officer_phone_number__html_name": "officer_phone_number",
        "officer_github_username__html_name": "officer_github_username",
        "officer_fav_course_1__html_name": "officer_fav_course_1",
        "officer_fav_course_2__html_name": "officer_fav_course_2",
        "officer_fav_language_1__html_name": "officer_fav_language_1",
        "officer_fav_language_2__html_name": "officer_fav_language_2",
        "officer_bio__html_name": "officer_bio",

        "sfuid__html_value": request.user.username,

    })
    "name_value" from new_officer_obj if new_officer_info_from_form does not have it  else from new_officer_info_from_form
    "announcement_emails__html_value" new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term but if officer_from_previous_term does not have it, then Nothing
    "gmail__html_value"new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing
    "phone_number__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing
    "github_username__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing

    "course1__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing
    "course2__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing
    "language1__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing
    "language2__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing
    "bio__html_value"  new_officer_info_from_form if  new_officer_info_from_form has it, otherwise officer_from_previous_term if it has it, otherwise Nothing

    if new_officer_info_from_form is not None:
        context.update({
            "name__html_value": new_officer_info_from_form['name'],
            "announcement_emails__html_value": new_officer_info_from_form['email'],
            "gmail__html_value": new_officer_info_from_form['gmail'],
            "phone_number__html_value": new_officer_info_from_form['phone_number'],
            "github_username__html_value": new_officer_info_from_form['github_username'],
            "course1__html_value": new_officer_info_from_form['course1'],
            "course2__html_value": new_officer_info_from_form['course2'],
            "language1__html_value": new_officer_info_from_form['language1'],
            "language2__html_value": new_officer_info_from_form['language2'],
            "bio__html_value": new_officer_info_from_form['bio']
        })
    elif officer_from_previous_term is not None:
        officer = Officer.objects.all().filter(
            sfuid=officer_from_previous_term.sfu_computing_id
        ).order_by('-elected_term').first()
        if officer is not None:
            context.update({
                "name__html_value": officer.name,
                "announcement_emails__html_value": ",".join(officer.announcementemailaddress_set.all()),
                "gmail__html_value": officer.gmail,
                "phone_number__html_value": officer.phone_number,
                "github_username__html_value": officer.github_username,
                "course1__html_value": officer.course1,
                "course2__html_value": officer.course2,
                "language1__html_value": officer.language1,
                "language2__html_value": officer.language2,
                "bio__html_value": officer.bio
            })
    if officer_from_previous_term is not None:
        context.update({
            "sfuid_email_alias__html_value": get_email_list(officer_from_previous_term.sfu_computing_id),
            "term__html_value": officer_from_previous_term.term.term,
            "year__html_value": officer_from_previous_term.term.year,
            "position_name__html_value": officer_from_previous_term.position_name,
            "date__html_value": officer_from_previous_term.start_date,
            "name_value": context["name_value"] if "name_value" in context else officer_from_previous_term.full_name
        })


def get_email_list(sfuid):
    response = requests.get(
        f"https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/datastore2/global/"
        f"accountInfo.js?username={sfuid}&art={settings.SFU_ENDPOINT_TOKEN}"
    )
    if response.status_code == 200:
        return json.loads(response.text)['aliases'][0]
