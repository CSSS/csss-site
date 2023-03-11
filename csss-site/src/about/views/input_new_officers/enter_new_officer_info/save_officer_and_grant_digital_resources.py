import datetime

from about.models import OfficerEmailListAndPositionMapping, Officer, AnnouncementEmailAddress
from about.views.Constants import UNPROCESSED_OFFICER_PHONE_NUMBER_KEY, UNPROCESSED_OFFICER_NAME__KEY, \
    UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY, \
    UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, UNPROCESSED_OFFICER_GMAIL__KEY, UNPROCESSED_OFFICER_COURSE_1__KEY, \
    UNPROCESSED_OFFICER_COURSE_2__KEY, \
    UNPROCESSED_OFFICER_LANGUAGE_1__KEY, UNPROCESSED_OFFICER_LANGUAGE_2__KEY, UNPROCESSED_OFFICER_BIO__KEY, \
    OFFICER_START_DATE_FORMAT
from about.views.input_new_officers.enter_new_officer_info.grant_digital_resource_access.assign_discord_roles import \
    assign_discord_roles
from about.views.input_new_officers.enter_new_officer_info.grant_digital_resource_access.grant_github_access import \
    grant_github_access
from about.views.input_new_officers.enter_new_officer_info.grant_digital_resource_access. \
    grant_google_drive_access import \
    grant_google_drive_access
from about.views.input_new_officers.enter_new_officer_info.notifications. \
    send_notifications_with_documentation_links import \
    send_notifications_with_documentation_links
from about.views.input_new_officers.enter_new_officer_info.utils.alert_sys_admin_to_update_email_list import \
    alert_sys_admin_to_update_email_list
from about.views.input_new_officers.enter_new_officer_info.utils.get_discord_username_and_nickname import \
    get_discord_username_and_nickname
from about.views.input_new_officers.enter_new_officer_info.utils.get_sfu_info import get_sfu_info
from about.views.utils.get_officer_image_path import get_officer_image_path
from csss.setup_logger import Loggers


def save_officer_and_grant_digital_resources(officer_emaillist_and_position_mappings, unprocessed_officer,
                                             officer_info):
    """
    Saves the new officer, gives the officer any access to digital resources that it may need
     and send them any relevant notifications regarding documentation

    Keyword Arguments
    officer_emaillist_and_position_mappings -- the queryset of currently saved position infos
    unprocessed_officer -- the UnprocessedOfficer object for the new officer to save
    officer_info -- dict containing the info for the officer that they themselves inputted

    Return
    bool -- False if there was a problem giving the user any necessary google drive, github access or discord roles
     or sending them their notifications in  gmail or discord DM
    error_message -- the error message if there was a problemw with any of the above
    """
    logger = Loggers.get_logger()
    position_name = unprocessed_officer.position_name
    phone_number = officer_info[UNPROCESSED_OFFICER_PHONE_NUMBER_KEY]
    full_name = officer_info[UNPROCESSED_OFFICER_NAME__KEY]
    sfu_computing_id = unprocessed_officer.sfu_computing_id
    success, error_message, sfu_info = get_sfu_info(sfu_computing_id)
    if not success:
        return success, error_message
    sfu_email_alias = sfu_info['aliases'][0]
    announcement_emails = []
    if len(officer_info[UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY].strip()) > 1:
        announcement_emails = [
            announcement_email.strip() for announcement_email in
            officer_info[UNPROCESSED_OFFICER_ANNOUNCEMENT_EMAILS__KEY].split(",")
        ]
    github_username = officer_info.get(UNPROCESSED_OFFICER_GITHUB_USERNAME__KEY, None)
    gmail = officer_info.get(UNPROCESSED_OFFICER_GMAIL__KEY, None)
    start_date = unprocessed_officer.start_date
    term_obj = unprocessed_officer.term
    course1 = officer_info[UNPROCESSED_OFFICER_COURSE_1__KEY]
    course2 = officer_info[UNPROCESSED_OFFICER_COURSE_2__KEY]
    language1 = officer_info[UNPROCESSED_OFFICER_LANGUAGE_1__KEY]
    language2 = officer_info[UNPROCESSED_OFFICER_LANGUAGE_2__KEY]
    bio = officer_info[UNPROCESSED_OFFICER_BIO__KEY]
    position_mapping_for_new_officer = officer_emaillist_and_position_mappings.filter(position_name=position_name)
    if position_mapping_for_new_officer is None:
        return False, f"Could not locate the position mapping for {position_name}"
    position_mapping_for_new_officer = position_mapping_for_new_officer.first()
    position_index = position_mapping_for_new_officer.position_index
    sfu_officer_mailing_list_email = position_mapping_for_new_officer.email
    github_teams_to_add = position_mapping_for_new_officer.officerpositiongithubteammapping_set.all()
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()]"
        f" detected {len(github_teams_to_add)} github teams mapped to position {position_name}"
    )

    current_positions = officer_emaillist_and_position_mappings.filter(marked_for_deletion=False)
    officer_has_google_drive_access = position_name in get_position_names(current_positions.filter(google_drive=True))
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()] "
        f"{position_name} {'has' if officer_has_google_drive_access else 'does not have' } access to "
        f"google drive"
    )
    officer_is_executive_officer = position_name in get_position_names(
        current_positions.filter(executive_officer=True)
    )
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()] "
        f"{position_name} is {'' if officer_is_executive_officer else 'not ' }an executive officer"
    )
    officer_is_election_officer = position_name in get_position_names(current_positions.filter(election_officer=True))
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()] "
        f"{position_name} is {'' if officer_is_election_officer else 'not ' }an election officer"
    )
    officer_is_council_representative = position_name in get_position_names(
        current_positions.filter(sfss_council_rep=True))
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()] "
        f"{position_name} is {'' if officer_is_council_representative else 'not ' }the council rep"
    )
    officer_is_frosh_week_chair = position_name in get_position_names(current_positions.filter(frosh_week_chair=True))
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()] "
        f"{position_name} is {'' if officer_is_frosh_week_chair else 'not ' }the frosh week chair"
    )
    officer_is_discord_manager = position_name in get_position_names(current_positions.filter(discord_manager=True))
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()] "
        f"{position_name} is {'' if officer_is_discord_manager else 'not ' }the discord manager"
    )

    pic_path = get_officer_image_path(term_obj, full_name)
    logger.info(
        f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()]"
        f" pic_path set to {pic_path}"
    )

    if type(start_date) != datetime.datetime:
        # if taking in the start_date from the form that the new officers have to fill in
        start_date = datetime.datetime.strptime(start_date, OFFICER_START_DATE_FORMAT)
    success, error_message, discord_username, discord_nickname = get_discord_username_and_nickname(
        unprocessed_officer.discord_id
    )
    discord_nickname = discord_nickname if discord_nickname is not None else "NA"
    if not success:
        return success, error_message
    logger.info(
        "[about/save_officer_and_grant_digital_resources.py saving new officer with the following info"
        f"\n\tposition_name={position_name}\n\tposition_index={position_index}\n\t"
        f"full_name={full_name}\n\tsfu_computing_id={sfu_computing_id}\n\tsfu_email_alias={sfu_email_alias}\n\t"
        f"phone_number={phone_number}\n\tgithub_username={github_username}\n\t"
        f"gmail={gmail}\n\tcourse1={course1}\n\tcourse2={course2}\n\tlanguage1={language1}\n\t"
        f"language2={language2}\n\tpic_path={pic_path}\n\tterm_obj={term_obj}\n\t"
        f"sfu_officer_mailing_list_email={sfu_officer_mailing_list_email}\n\tstart_date={start_date}\n\t"
        f"unprocessed_officer.discord_id={unprocessed_officer.discord_id}\n\t"
        f"discord_username={discord_username}\n\tdiscord_nickname={discord_nickname}"
    )
    officer_obj = Officer(
        position_name=position_name, position_index=position_index, full_name=full_name,
        sfu_computing_id=sfu_computing_id, sfu_email_alias=sfu_email_alias, phone_number=phone_number,
        github_username=github_username, gmail=gmail, course1=course1, course2=course2, language1=language1,
        language2=language2, bio=bio, image=pic_path, elected_term=term_obj,
        sfu_officer_mailing_list_email=sfu_officer_mailing_list_email, start_date=start_date,
        discord_id=unprocessed_officer.discord_id, discord_username=discord_username,
        discord_nickname=discord_nickname
    )

    success, error_message = grant_google_drive_access(officer_has_google_drive_access, gmail)
    if not success:
        return success, error_message
    if officer_has_google_drive_access:
        logger.info(
            f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()]"
            f" granted google drive access to {gmail} for position {position_name}"
        )

    success, error_message = grant_github_access(officer_obj, github_teams_to_add)
    if not success:
        return success, error_message
    if len(github_teams_to_add) > 0:
        github_teams = "], [".join([github_team.get_team_name() for github_team in github_teams_to_add])
        logger.info(
            f"[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()]"
            f" granted {officer_obj.github_username} access to github teams [{github_teams}]"
            f" for position {position_name}"
        )
    success, error_message = assign_discord_roles(
        position_mapping_for_new_officer.discord_role_name, unprocessed_officer.discord_id, term_obj
    )
    if not success:
        return success, error_message
    success, error_message = send_notifications_with_documentation_links(
        officer_obj, officer_is_executive_officer, officer_is_election_officer, officer_is_council_representative,
        officer_is_frosh_week_chair, officer_is_discord_manager
    )
    if not success:
        return success, error_message
    alert_sys_admin_to_update_email_list(sfu_officer_mailing_list_email)
    if not success:
        return success, error_message
    officer_obj.save()
    for email in announcement_emails:
        AnnouncementEmailAddress(email=email, officer=officer_obj).save()
    logger.info("[about/save_officer_and_grant_digital_resources.py save_officer_and_grant_digital_resources()]"
                " successfully saved the officer and set their digital resources")
    return True, None


def get_position_names(query_result):
    return list(
        query_result.values_list(
            f'{OfficerEmailListAndPositionMapping.position_name.field_name}', flat=True
        )
    )
