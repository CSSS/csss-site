import collections
import csv
import datetime
import json
import logging
import re

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render

from about.models import Term, Officer, AnnouncementEmailAddress, OfficerEmailListAndPositionMapping
from about.views.Constants import TAB_STRING
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.Gmail import Gmail
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_uploading_and_download_officer_lists
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import TERM_SEASONS
from resource_management.models import OfficerPositionGithubTeamMapping
from resource_management.views.resource_apis.github.github_api import GitHubAPI

YEAR_AND_TERM_COLUMN = 0
POSITION_COLUMN = 0
NAME_COLUMN = 1
SFU_ID_COLUMN = 2
SFU_EMAIL_ALIAS_COLUMN = 3
ANNOUNCEMENT_EMAILS_COLUMN = 4
PHONE_NUMBER_COLUMN = 5
GITHUB_USER_NAME_COLUMN = 6
GITHUB_TEAM_MEMBERSHIPS_COLUMN = 7
GMAIL_COLUMN = 8
START_DATE_COLUMN = 9
FAVORITE_COURSES_COLUMN = 10
FAVORITE_LANGUAGES_COLUMN = 11
BIO_COLUMN = 12


ELECTION_OFFICER_POSITIONS = ["By-Election Officer", "General Election Officer"]
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE = ["SFSS Council-Representative"]
OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE.extend(ELECTION_OFFICER_POSITIONS.copy())

logger = logging.getLogger('csss_site')


def show_page_for_uploading_officer_list(request):
    """
    Show page where the officer can upload an officer list
    """
    return render(
        request,
        'about/upload_list.html',
        create_context_for_uploading_and_download_officer_lists(request, tab=TAB_STRING)
    )


def process_officer_list_upload(request):
    """
    Takes in a JSON or CSV with the list of officers to save
    """
    context = create_context_for_uploading_and_download_officer_lists(request, tab=TAB_STRING)
    overwrite = 'overwrite' in request.POST
    error_message = None
    if request.method == "POST":
        if 'csv' in request.FILES:
            return save_officers_in_csv(request, overwrite, context)
        if 'years_json' in request.FILES:
            uploaded_file = request.FILES['years_json']
            fs = FileSystemStorage()
            file_name = fs.save(uploaded_file.name, uploaded_file)
            with open(fs.url(file_name), 'r') as json_file:
                officer_json = json.loads(json_file.read())
                error_message = save_yearly_document(officer_json, overwrite)
        if 'term_json' in request.FILES:
            uploaded_file = request.FILES['term_json']
            fs = FileSystemStorage()
            file_name = fs.save(uploaded_file.name, uploaded_file)
            with open(fs.url(file_name), 'r') as json_file:
                officer_json = json.loads(json_file.read())
                if 'year' in officer_json and 'term' in officer_json and 'officers' in officer_json:
                    year = officer_json['year']
                    term = officer_json['term']
                    error_message = iterate_through_officers_for_term(overwrite, year, term, officer_json['officers'])
    if error_message is not None:
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'about/upload_list.html', context)
    return HttpResponseRedirect(f'{settings.URL_ROOT}about/list_of_officers')


def save_officers_in_csv(request, overwrite, context):
    """
    Saved the officers specified in the csv

    Keyword Argument
    request -- the django request object
    overwrite -- indicates whether or not to remove the officer under a term if that term appears in the csv

    Return
    render value -- sends user to appropriate page based on if there was an error
    """
    year = 0
    term = 0
    output = collections.OrderedDict()
    uploaded_file = request.FILES['csv']
    fs = FileSystemStorage()
    file_name = fs.save(uploaded_file.name, uploaded_file)
    with open(fs.path(file_name)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            if re.match(fr"{'|'.join(TERM_SEASONS)} \d\d\d\d", row[YEAR_AND_TERM_COLUMN]):  # noqa: W605
                year = (row[YEAR_AND_TERM_COLUMN].strip()[row[YEAR_AND_TERM_COLUMN].strip().find(" "):]).strip()
                term = row[YEAR_AND_TERM_COLUMN].strip()[:row[YEAR_AND_TERM_COLUMN].strip().find(" ")].strip()
            logger.info(
                f"[about/import_export_officer_lists save_officers_in_csv()] going through term {term} {year}"
            )
            if row[NAME_COLUMN] != "" and row[NAME_COLUMN] != "Name":
                if year not in output:
                    output[year] = {}
                if term not in output[year]:
                    output[year][term] = []
                success, member, error_message = return_member_json(row)
                if not success:
                    context[ERROR_MESSAGES_KEY] = [error_message]
                    return render(request, 'about/upload_list.html', context)
                output[year][term].append(member)
        output = collections.OrderedDict(reversed(list(output.items())))
        for key, value in output.items():
            output[key] = collections.OrderedDict(reversed(list(output[key].items())))
        error_message = save_yearly_document(output, overwrite)
    if error_message is not None:
        context[ERROR_MESSAGES_KEY] = [error_message]
        return render(request, 'about/upload_list.html', context)
    return HttpResponseRedirect(f'{settings.URL_ROOT}about/list_of_officers')


def return_member_json(row):
    """
    takes in a row of a csv and creates and returns a JSON representation of the officer on that row

    Keyword Argument
    row -- the row that contain the officer info

    Return
    Bool -- true or false if it was able to extract the officer
    member -- the dict that represents the member
    error_message -- the error message if there was a problem with one or more of the officer fields
    """
    course_divider = row[FAVORITE_COURSES_COLUMN].find("|")
    language_divider = row[FAVORITE_LANGUAGES_COLUMN].find("|")
    member = {
        "officer_position": row[POSITION_COLUMN],
        "name": row[NAME_COLUMN],
        "sfu_computing_id": row[SFU_ID_COLUMN],
        "sfu_email_alias": row[SFU_EMAIL_ALIAS_COLUMN],
        "phone_number": int(0 if row[PHONE_NUMBER_COLUMN] == "" else row[PHONE_NUMBER_COLUMN]),
        'github_username': row[GITHUB_USER_NAME_COLUMN],
        'gmail': row[GMAIL_COLUMN],
        "start_date": row[START_DATE_COLUMN],
        'fav_course_1': row[FAVORITE_COURSES_COLUMN][:course_divider - 1] if course_divider != -1
        else row[FAVORITE_COURSES_COLUMN],
        'fav_course_2': row[FAVORITE_COURSES_COLUMN][course_divider + 2:] if course_divider != -1 else "",
        'fav_language_1': row[FAVORITE_LANGUAGES_COLUMN][:language_divider - 1] if language_divider != -1
        else row[FAVORITE_LANGUAGES_COLUMN],
        'fav_language_2': row[FAVORITE_LANGUAGES_COLUMN][language_divider + 2:] if language_divider != -1 else "",
        'bio': row[BIO_COLUMN].replace("[comma]", ",").replace("\\n", "<br/>")
    }
    if not re.match(r"\d\d\d\d-\d\d-\d\d", member["start_date"]):  # noqa: W605
        error_message = f"invalid start date of '{member['start_date']}' for officer '{member['name']}' specified"
        logger.info(f"[about/import_export_officer_lists return_member_json()] {error_message}")
        return False, None, error_message
    if len(member['github_username']) == 0:
        member['github_teams'] = []
    else:
        member["github_teams"] = extract_multiple_values_from_csv_column(
            row[GITHUB_TEAM_MEMBERSHIPS_COLUMN],
            default_value="officers"
        )
    member["announcement_emails"] = extract_multiple_values_from_csv_column(row[ANNOUNCEMENT_EMAILS_COLUMN])
    logger.info(f"[about/import_export_officer_lists return_member_json()] returning member {member}")
    return True, member, None


def extract_multiple_values_from_csv_column(column, default_value=None, delimiter="|"):
    """
    Extracts multiple values from a csv column with the specified delimiter

    Keyword Argument
    row -- column that contains potential multiple values
    default_value -- the value that needs to be added to return array no matter what else is in the column
    delimiter -- the delimiter to split the column on, "|" by default

    return
    an array of all the values extracts from csv column
    """
    values = [value.strip() for value in column.split(delimiter)]
    #  the above code set values to [""] if the indicated row is empty
    # which trigger the below if statement
    if len(values) == 1 and values[0] == "":
        if default_value is not None:
            logger.info(f"[about/import_export_officer_lists extract_multiple_values_from_csv_column()] "
                        f"returning values {[default_value]}")
            return [default_value]
        else:
            logger.info("[about/import_export_officer_lists extract_multiple_values_from_csv_column()] "
                        "returning no values")
            return []
    else:
        if default_value is not None:
            values.append(default_value)
    logger.info(f"[about/import_export_officer_lists extract_multiple_values_from_csv_column()] "
                f"returning values {values}")
    return values


def save_yearly_document(officer_json, overwrite):
    """
    Saves the officers in the json to the website

    Keyword Argument
    officer_json -- a json of officers that can support multiple years and term
    overwrite -- indicates whether or not to delete the officer that already exist under
     any of the terms specified in the JSON

    Return
    error_message -- the error_message if there was one or just None otherwise
    """
    current_year = datetime.date.today().year
    for year in range(1984, current_year + 1):
        year = f"{year}"
        if year in officer_json:
            logger.info(f"[about/import_export_officer_lists save_yearly_document()] "
                        f"iterating through year {year}")
            officers_in_year = officer_json[year]
            for term in TERM_SEASONS:
                if term in officers_in_year:
                    logger.info(f"[about/import_export_officer_lists save_yearly_document()] "
                                f"iterating through term {term}")
                    error_message = iterate_through_officers_for_term(
                        overwrite, year, term,
                        officers_in_year[term]
                    )
                    if error_message is not None:
                        return error_message
    return None


def iterate_through_officers_for_term(overwrite, year, term, officers_in_term):
    """
    Iterate through the officers in a specific term and save them to the website

    Keyword Argument
    overwrite -- indicates whether or not to delete the officer that already exist under any of the terms
    specified in the JSON
    year -- the year in YYYY format
    term -- the season that the term takes place in, e.g. Spring, Summer or Fall
    officers_in_term -- a dictionary of the officers for the specified term

    Return
    error_message -- error message if there was a problem, otherwise None
    """
    if overwrite:
        term = create_new_term(year, term)
    else:
        term = save_new_term(year, term)
    position_index = -1
    previous_position = ""
    for officer in officers_in_term:
        if officer['officer_position'] != previous_position:
            position_index += 1
        previous_position = officer['officer_position']
        success, error_message = extract_and_save_officer_info(term, officer, position_index)
        if not success:
            return error_message
    return None


def create_new_term(year, term):
    """
    create the specified term or deletes all the officers under the term if it exists

    Keyword Argument
    year -- the year in YYYY format
    term -- the season that the term takes place in, e.g. Spring, Summer or Fall

    return
    term_obj -- the term that was created with the specified year and season
    """
    term_number = get_term_number(year, term)
    term_obj = Term.objects.all().filter(term=term, term_number=term_number, year=int(year))
    if len(term_obj) == 0:
        logger.info(f"[about/import_export_officer_lists create_new_term()] "
                    f"create new term for {term} {year}")
        term_obj = Term(term=term, term_number=term_number, year=int(year))
        term_obj.save()
    else:
        term_obj = term_obj[0]
        logger.info(f"[about/import_export_officer_lists create_new_term()] "
                    f"deleting all offcers under term {term} {year}")
        officers = Officer.objects.all().filter(elected_term=term_obj)
        for officer in officers:
            officer.delete()
    return term_obj


def extract_and_save_officer_info(term_obj, officer, position_index):
    """
    saves the officer specified in the officer dictionary

    Keyword Argument
    term_obj -- the term that the officer needs to be saved under
    officer -- the officer that needs to be saved
    position_index -- the index for the officer that needs to be saved

    Return
    success -- True or False
    error_message - error message if not successful, otherwise None
    """
    phone_number = officer['phone_number']
    position_name = officer['officer_position']
    full_name = officer['name']
    sfu_computing_id = officer['sfu_computing_id']
    sfu_email_alias = officer['sfu_email_alias']
    announcement_emails = officer['announcement_emails']
    github_username = officer['github_username']
    gmail = officer['gmail']
    start_date = datetime.datetime.strptime(officer['start_date'], "%Y-%m-%d")
    fav_course_1 = officer['fav_course_1']
    fav_course_2 = officer['fav_course_2']
    fav_language_1 = officer['fav_language_1']
    fav_language_2 = officer['fav_language_2']
    bio = officer['bio']
    sfu_officer_mailing_list_email = "NONE"
    # github_teams = officer['github_teams']
    success, error_message = save_officer_and_grant_digital_resources(
        phone_number, full_name, sfu_computing_id, sfu_email_alias, announcement_emails, github_username,
        gmail, start_date, fav_course_1, fav_course_2, fav_language_1,
        fav_language_2, bio, position_name, position_index, term_obj,
        sfu_officer_mailing_list_email,
        apply_github_team_memberships=False
    )
    return success, error_message


def get_term_number(year, term_season):
    """
    gets the term number using the year and term

    Keyword Arguments
    year -- the current year in YYYY format
    term_season -- the season that the term takes place in, e.g. Spring, Summer or Fall

    returns the term_number, which is in the format YYYY<1/2/3>, or None if year is not a number
     or specified season does not exist
    """
    return None \
        if ((not f"{year}".isdigit()) or term_season not in TERM_SEASONS) \
        else int(year) * 10 + _get_term_season_number(term_season)


def _get_term_season_number(term_season):
    """
    Gets the term number using the specified season

    Keyword Arguments
    term -- the term object that the function will return its number

    Returns
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be None if the
        term does not have a valid season
    """
    for (idx, term_choice) in enumerate(Term.term_choices):
        if term_season == term_choice[0]:
            return idx
    return None


def save_new_term(year, term_season):
    """
    either saves a new term with the given year and term or just returns an existing term that matches that given
    year and term

    Keyword Arguments
    year -- the year in YYYY format
    term -- the season that the term takes place in, e.g. Spring, Summer or Fall

    Return
    term_obj -- the term object that corresponds to given year and term
     or None if proper term year and season not specified
    """
    term_number = get_term_number(year, term_season)
    if term_number is None:
        return None
    term_obj, created = Term.objects.get_or_create(
        term=term_season,
        term_number=term_number,
        year=int(year)
    )
    return term_obj


def save_officer_and_grant_digital_resources(phone_number, full_name, sfu_computing_id, sfu_email_alias,
                                             announcement_emails, github_username, gmail, start_date, fav_course_1,
                                             fav_course_2, fav_language_1, fav_language_2, bio, position_name,
                                             position_index, term_obj, sfu_officer_mailing_list_email,
                                             apply_github_team_memberships=True,
                                             gdrive_api=None,
                                             send_email_notification=False):
    """
    Saves the officer with all the necessary info and gives them access to digital resources
     if flags indicate that they should be given access

    Keyword Argument
    phone_number -- officer's phone number
    full_name -- the officer's full name
    sfu_computing_id -- the officer's SFUID
    sfu_email_alias -- the officer's sfu email alias
    announcement_emails -- all the emails that the officer may use for sending out SFU CSSS emails to the students
    github_username -- the officer's github username
    gmail -- the officer's gmail
    start_date -- the date that the officer started their current term of their position
    fav_course_1 -- the officer's first fav course
    fav_course_2 -- the officer's second fav course
    fav_language_1 -- the officer's first fav language
    fav_language_2 -- the officer's second fav language
    bio -- the officer's bio that is already in html markdown form
    position_name -- the name for the officer's position
    position_index -- the index for the officer's position
    term_obj -- the term that the officer's info is being saved for
    sfu_officer_mailing_list_email -- the sfu email list that the officer will be contact-able at
    remove_from_naughty_list -- indicates whether or not to remove the officer from the list
     that determines whether or not to keep their name in the list that prevents them from
     gaining access to CSSS resources
    apply_github_team_memberships -- indicates whether or not the officer needs to be given github access
    gdrive_api -- the google drive object that is used to communicate with the google drive API
    gitlab_api -- the SFU gitlab object that is used to communicate with the SFU gitlab API
    send_email_notifications -- indicates whether or not to send an email to the officer's SFU email with instruction

    Returns
    success - true or False
    error_message -- error message if success is False
    """

    pic_path = get_officer_image_path(term_obj, full_name)
    logger.info(
        f"[about/officer_management_helper.py save_officer_and_grant_digital_resources()] pic_path set to {pic_path}")

    if type(start_date) != datetime.datetime:
        # if taking in the start_date from the form that the new officers have to fill in
        start_date = datetime.datetime.strptime(start_date, "%A, %d %b %Y %I:%m %S %p")

    officer_obj = Officer(
        position_name=position_name, position_index=position_index, full_name=full_name,
        sfu_computing_id=sfu_computing_id, sfu_email_alias=sfu_email_alias, phone_number=phone_number,
        github_username=github_username, gmail=gmail, course1=fav_course_1, course2=fav_course_2,
        language1=fav_language_1, language2=fav_language_2, bio=bio, image=pic_path, elected_term=term_obj,
        sfu_officer_mailing_list_email=sfu_officer_mailing_list_email, start_date=start_date
    )

    logger.info(
        "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
        f"saved user term={term_obj} full_name={full_name} position_name={position_name}"
    )

    officer_obj.save()

    for email in announcement_emails:
        AnnouncementEmailAddress(email=email, officer=officer_obj).save()

    if position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
        if gdrive_api is not None:
            logger.info(
                "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
                f"giving user {officer_obj} access to CSSS google drive"
            )
            success, file_name, error_message = gdrive_api.add_users_gdrive([gmail])
            if not success:
                officer_obj.delete()
                return success, error_message

    if apply_github_team_memberships:
        success, error_message = _save_officer_github_membership(officer_obj)
        if not success:
            officer_obj.delete()
            return success, error_message
    subject = "Welcome to the CSSS"
    body = None
    if send_email_notification:
        logger.info(
            "[about/officer_management_helper.py save_officer_and_grant_digital_resources()] "
            f"sending email notification to user {officer_obj} who is in the officer position {position_name}"
        )
        if position_name not in OFFICERS_THAT_DO_NOT_HAVE_EYES_ONLY_PRIVILEGE:
            body = (
                f"Hello {full_name},\n\n"
                "Congrats on becoming a CSSS Officer,\n\n"
                "Please make sure that you\n\n"
                " 1. check the email associated with your github for an invitation to our SFU CSSS Github org on "
                "Github\n "
                " 2. check your sfu email for an invitation to join our SFU CSSS org on SFU Gitlab\n\n"
                "Apart from that, take the following documentation, which is linked here, as it is a "
                "nightmare trying to figure out "
                "markdown for gmail from a python script: https://github.com/CSSS/documents/wiki"
            )
        elif position_name in ELECTION_OFFICER_POSITIONS:
            body = (
                f"Hello {full_name},\n\n"
                "Congrats on becoming a CSSS Election Officer,\n\n"
                "Please read the following documentation, which is linked here, "
                "as it is a nightmare trying to figure out "
                "markdown for gmail from a python script: https://github.com/CSSS/elections-documentation"
            )
        if body is not None:
            # only sending an email if the new officer got a body which only happens if the user was granted access
            # to any csss digital resources
            gmail = Gmail()
            if not gmail.connection_successful:
                return False, gmail.error_message
            success, error_message = gmail.send_email(
                subject, body, f"{sfu_computing_id}@sfu.ca", full_name, "SFU CSSS Website"
            )
            if not success:
                return False, error_message
            success, error_message = gmail.close_connection()
            if not success:
                officer_obj.delete()
                return success, error_message
    return True, None


def _save_officer_github_membership(officer):
    """
    Adds the officers to the necessary github teams.

    Keyword Arguments
    officer -- the officer to add to the github teams

    return
    success -- true or false Bool
    error_message -- the error_message if success is False or None otherwise
    """
    position_mapping = OfficerEmailListAndPositionMapping.objects.all().filter(
        position_index=officer.position_index
    )
    if len(position_mapping) == 0:
        error_message = f"could not find any position mappings for position_index {officer.position_index}"
        logger.info(f"[about/officer_management_helper.py _save_officer_github_membership()] {error_message}")
        return False, error_message

    github_api = GitHubAPI()
    if github_api.connection_successful is False:
        logger.info("[about/officer_management_helper.py _save_officer_github_membership()]"
                    f" {github_api.error_message}")
        return False, f"{github_api.error_message}"
    github_team_mappings = OfficerPositionGithubTeamMapping.objects.all().filter(
        officer_position_mapping=position_mapping[0]
    )
    for github_team_mapping in github_team_mappings:
        success, error_message = github_api.add_users_to_a_team(
            [officer.github_username],
            github_team_mapping.github_team.team_name
        )
        if not success:
            logger.info(
                "[about/officer_management_helper.py _save_officer_github_membership()] "
                f"unable to add officer {officer.github_username} to team"
                f" {github_team_mapping.github_team.team_name} due to error {error_message}"
            )
            return False, error_message
        logger.info(
            "[about/officer_management_helper.py _save_officer_github_membership()] "
            f"mapped officer {officer} to team {github_team_mapping.github_team.team_name}"
        )
    return True, None
