from about.models import Officer, OfficerEmailListAndPositionMapping, AnnouncementEmailAddress
from about.views.create_context.enter_officer_info.create_context_for_enter_officer_info_html import get_email_list
from about.views.officer_position_and_github_mapping.officer_management_helper import get_officer_image_path


def save_new_officer(new_officer_info, new_officer):
    officer_email_list_and_position_mapping = OfficerEmailListAndPositionMapping.objects.all().get(
        position_name=new_officer_info.position_name
    )
    officer_obj = Officer(
        position_name=new_officer_info.position_name,
        position_index=officer_email_list_and_position_mapping.position_index,
        name=new_officer_info['name'], start_date=new_officer.start_date, sfuid=new_officer.sfu_computing_id,
        sfu_email_alias=get_email_list(new_officer.sfu_computing_id), phone_number=new_officer_info['phone_number'],
        github_username=new_officer_info['github_username'], gmail=new_officer_info['gmail'],
        course1=new_officer_info['course1'], course2=new_officer_info['course2'],
        language1=new_officer_info['language1'],
        language2=new_officer_info['language2'], bio=new_officer_info['bio'],
        image=get_officer_image_path(new_officer.term, new_officer_info['name']),
        elected_term=new_officer.term, sfu_officer_mailing_list_email=officer_email_list_and_position_mapping.email
    )
    officer_obj.save()
    for announcement_email in new_officer_info['announcement_emails'].split(","):
        announcement_email = announcement_email.strip()
        AnnouncementEmailAddress(email=announcement_email, officer=officer_obj).save()
