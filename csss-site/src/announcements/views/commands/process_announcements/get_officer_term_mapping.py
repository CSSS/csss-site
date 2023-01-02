from about.models import AnnouncementEmailAddress, Term, Officer


def get_officer_term_mapping():
    """
    creates a dictionary containing all relevant emails for all terms

    return
    officer_mapping - a dictionary where the key is the term number (e.g. 20202)
    and the values is a list of valid emails
    """
    officer_mapping = {}
    for term in Term.objects.all().order_by('term_number'):
        term_number = f"{term.term_number}"
        for officer in Officer.objects.all().filter(elected_term=term):
            if term_number not in officer_mapping:
                officer_mapping[term_number] = []
            officer_sfu_computing_id_not_in_mapping = (
                len(officer.sfu_computing_id) > 0 and
                f"{officer.sfu_computing_id}@sfu.ca" not in officer_mapping[term_number]
            )
            if officer_sfu_computing_id_not_in_mapping:
                officer_mapping[term_number].append(f"{officer.sfu_computing_id}@sfu.ca")
            officer_email_alias_not_in_mapping = (
                len(officer.sfu_email_alias) > 0 and
                f"{officer.sfu_email_alias}@sfu.ca" not in officer_mapping[term_number]
            )
            if officer_email_alias_not_in_mapping:
                officer_mapping[term_number].append(f"{officer.sfu_email_alias}@sfu.ca")
            for announcement_emails in AnnouncementEmailAddress.objects.all().filter(officer=officer):
                if announcement_emails.email not in officer_mapping[term_number]:
                    officer_mapping[term_number].append(announcement_emails.email)
    return officer_mapping
