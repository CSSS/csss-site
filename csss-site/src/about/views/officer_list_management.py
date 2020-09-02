import collections
import csv
import datetime
import json
import logging
import re
from datetime import date

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.views.save_officer_and_terms import save_new_term, create_new_term, save_officer_and_grant_digital_resources
from csss.views_helper import verify_access_logged_user_and_create_context, ERROR_MESSAGE_KEY
from resource_management.models import OfficerGithubTeam

logger = logging.getLogger('csss_site')

TAB_STRING = "about"

YEAR_AND_TERM_COLUMN = 0
POSITION_COLUMN = 0
NAME_COLUMN = 1
SFU_ID_COLUMN = 2
ANNOUNCEMENT_EMAILS_COLUMN = 3
PHONE_NUMBER_COLUMN = 4
GITHUB_USER_NAME_COLUMN = 5
GITHUB_TEAM_MEMBERSHIPS_COLUMN = 6
GMAIL_COLUMN = 7
START_DATE_COLUMN = 8
FAVORITE_COURSES_COLUMN = 9
FAVORITE_LANGUAGES_COLUMN = 10
BIO_COLUMN = 11

ACADEMIC_TERMS = ["Spring", "Summer", "Fall"]


def show_page_for_uploading_officer_list(request):
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    return render(request, 'about/officer_list_management/upload_list.html', context)


def process_officer_list_upload(request):
    (render_value, error_message, context) = verify_access_logged_user_and_create_context(request, TAB_STRING)
    if context is None:
        request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
        return render_value
    overwrite = 'overwrite' in request.POST
    if request.method == "POST":
        if 'csv' in request.FILES:
            year = 0
            term = 0
            output = collections.OrderedDict()
            uploaded_file = request.FILES['csv']
            fs = FileSystemStorage()
            file_name = fs.save(uploaded_file.name, uploaded_file)
            # with open(fs.url(file_name)) as csv_file:
            with open(fs.path(file_name)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                for row in csv_reader:
                    if re.match(f"{'|'.join(ACADEMIC_TERMS)} \d\d\d\d", row[YEAR_AND_TERM_COLUMN]):
                        year = (row[YEAR_AND_TERM_COLUMN].strip()[row[YEAR_AND_TERM_COLUMN].strip().find(" "):]).strip()
                        term = row[YEAR_AND_TERM_COLUMN].strip()[:row[YEAR_AND_TERM_COLUMN].strip().find(" ")].strip()
                    logger.info(f"going through term {term} {year}")
                    if row[NAME_COLUMN] != "" and row[NAME_COLUMN] != "Name":
                        if year not in output:
                            output[year] = {}
                        if term not in output[year]:
                            output[year][term] = []
                        success, member, error_message = get_member(row)
                        if not success:
                            request.session[ERROR_MESSAGE_KEY] = '{}<br>'.format(error_message)
                            return HttpResponseRedirect('/error')
                        output[year][term].append(member)
                output = collections.OrderedDict(reversed(list(output.items())))
                for key, value in output.items():
                    output[key] = collections.OrderedDict(reversed(list(output[key].items())))
                save_yearly_document(output, overwrite)
        if 'years_json' in request.FILES:
            uploaded_file = request.FILES['years_json']
            fs = FileSystemStorage()
            file_name = fs.save(uploaded_file.name, uploaded_file)
            with open(fs.url(file_name), 'r') as json_file:
                officer_json = json.loads(json_file.read())
                save_yearly_document(officer_json, overwrite)
        if 'term_json' in request.FILES:
            uploaded_file = request.FILES['term_json']
            fs = FileSystemStorage()
            file_name = fs.save(uploaded_file.name, uploaded_file)
            with open(fs.url(file_name), 'r') as json_file:
                officer_json = json.loads(json_file.read())
                if 'year' in officer_json and 'term' in officer_json and 'officers' in officer_json:
                    year = officer_json['year']
                    term = officer_json['term']
                    iterate_through_officers_for_term(overwrite, year, term, officer_json['officers'])
    return HttpResponseRedirect('/about/list_of_officers')


def get_member(row):
    course_divider = row[FAVORITE_COURSES_COLUMN].find("|")
    language_divider = row[FAVORITE_LANGUAGES_COLUMN].find("|")
    member = {
        "position_type": row[POSITION_COLUMN],
        "name": row[NAME_COLUMN],
        "sfuid": "jsaadatm",
        # "sfuid": row[SFU_ID_COLUMN],
        "phone_number": int(0 if row[PHONE_NUMBER_COLUMN] == "" else row[PHONE_NUMBER_COLUMN]),
        'github_username': "jackzhin33",
        # 'github_username': row[GITHUB_USER_NAME_COLUMN],
        'gmail': "jackzhin33@gmail.com",
        # 'gmail': row[GMAIL_COLUMN],
        "start_date": row[START_DATE_COLUMN],
        'fav_course_1': row[FAVORITE_COURSES_COLUMN][:course_divider - 1],
        'fav_course_2': row[FAVORITE_COURSES_COLUMN][course_divider + 2:],
        'fav_language_1': row[FAVORITE_LANGUAGES_COLUMN][:language_divider - 1],
        'fav_language_2': row[FAVORITE_LANGUAGES_COLUMN][language_divider + 2:],
        'bio': row[BIO_COLUMN].replace("[comma]", ",").replace("\\n", "<br/>")
    }
    if not re.match("\d\d\d\d-\d\d-\d\d", member["start_date"]):
        return False, None, f"invalid start date of '{member['start_date']}' for officer '{member['name']}' specified"
    if len(member['github_username']) == 0:
        member['github_teams'] = []
    else:
        member["github_teams"] = [team.strip() for team in row[GITHUB_TEAM_MEMBERSHIPS_COLUMN].split("|")]
        if len(member["github_teams"]) == 1 and member["github_teams"][0] == "":
            member["github_teams"] = ["officers"]
        else:
            member["github_teams"].append("officers")

    member["announcement_emails"] = [email.strip() for email in row[ANNOUNCEMENT_EMAILS_COLUMN].split("|")]
    if len(member["announcement_emails"]) == 1 and member["announcement_emails"][0] == "":
        member["announcement_emails"] = [f"{row[SFU_ID_COLUMN]}@sfu.ca" if len(row[SFU_ID_COLUMN]) > 0 else ""]
    else:
        member["announcement_emails"].append(f"{row[SFU_ID_COLUMN]}@sfu.ca" if len(row[SFU_ID_COLUMN]) > 0 else "")
    return True, member, None


def save_yearly_document(officer_json, overwrite):
    current_year = date.today().year
    for year in range(1984, current_year + 1):
        year = f"{year}"
        if year in officer_json:
            officers_in_year = officer_json[year]
            for valid_term in ACADEMIC_TERMS:
                if valid_term in officers_in_year:
                    iterate_through_officers_for_term(overwrite, year, valid_term, officers_in_year[valid_term])


def iterate_through_officers_for_term(overwrite, year, valid_term, officers_in_term):
    if overwrite:
        term = create_new_term(year, valid_term)
    else:
        term = save_new_term(year, valid_term)
    position_index = -1
    previous_position = ""
    for officer in officers_in_term:
        if officer['position_type'] != previous_position:
            position_index += 1
        previous_position = officer['position_type']
        extract_and_save_officer_info(term, officer, position_index)


def extract_and_save_officer_info(term_obj, officer, position_index):
    phone_number = officer['phone_number']
    position_type = officer['position_type']
    full_name = officer['name']
    full_name_in_pic = officer['name'].replace(" ", "_")
    sfuid = officer['sfuid']
    announcement_emails = officer['announcement_emails']
    github_username = officer['github_username']
    gmail = officer['gmail']
    start_date = datetime.datetime.strptime(officer['start_date'], "%Y-%m-%d")
    fav_course_1 = officer['fav_course_1']
    fav_course_2 = officer['fav_course_2']
    fav_language_1 = officer['fav_language_1']
    fav_language_2 = officer['fav_language_2']
    bio = officer['bio']
    officer_obj = save_officer_and_grant_digital_resources(term_obj, phone_number, position_type, full_name,
                                                           full_name_in_pic, sfuid, announcement_emails,
                                                           github_username,
                                                           gmail, start_date, fav_course_1, fav_course_2,
                                                           fav_language_1, fav_language_2, bio, position_index,
                                                           grant_digital_resources=False)
    for team in officer['github_teams']:
        OfficerGithubTeam(team_name=team, officer=officer_obj).save()
