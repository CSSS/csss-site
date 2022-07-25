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

from about.models import Term, Officer, OfficerEmailListAndPositionMapping, UnProcessedOfficer
from about.views.Constants import TAB_STRING
from about.views.input_new_officers.enter_new_officer_info.save_officer_and_grant_digital_resources import \
    save_officer_and_grant_digital_resources
from about.views.utils.get_term_season_number import get_term_season_number
from csss.views.context_creation.create_authenticated_contexts import \
    create_context_for_uploading_and_download_officer_lists
from csss.views.views import ERROR_MESSAGES_KEY
from csss.views_helper import TERM_SEASONS

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
    officer_emaillist_and_position_mappings = OfficerEmailListAndPositionMapping.objects.all()
    for officer in officers_in_term:
        if officer['officer_position'] != previous_position:
            position_index += 1
        previous_position = officer['officer_position']
        success, error_message = extract_and_save_officer_info(
            officer_emaillist_and_position_mappings, term, officer, position_index
        )
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


def extract_and_save_officer_info(officer_emaillist_and_position_mappings, term_obj, officer, position_index):
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
    position_name = officer['officer_position']
    sfu_computing_id = officer['sfu_computing_id']
    start_date = datetime.datetime.strptime(officer['start_date'], "%Y-%m-%d")
    unprocessed_officer = UnProcessedOfficer(
        position_name=position_name, sfu_computing_id=sfu_computing_id, start_date=start_date,
        term=term_obj, discord_id='1234'
    )
    success, error_message = save_officer_and_grant_digital_resources(
        officer_emaillist_and_position_mappings, unprocessed_officer, officer
    )
    return success, error_message


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
        else int(year) * 10 + get_term_season_number(term_season)
