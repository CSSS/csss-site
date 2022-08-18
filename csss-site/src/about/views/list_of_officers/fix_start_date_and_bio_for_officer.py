import datetime

import markdown


def fix_start_date_and_bio_for_officer(officer):
    """
    fix the start date and bio for the officers before showing them to the user
    The start date needs its time component removed

    Keyword Argument
    officer -- the officer whose start date needs to be changed

    Return
    officer -- the officer whose start date's time was removed
    """
    officer.start_date = datetime.datetime.strftime(officer.start_date, "%d %b %Y")
    officer.bio = markdown.markdown(
        officer.bio, extensions=['sane_lists', 'markdown_link_attr_modifier'],
        extension_configs={
            'markdown_link_attr_modifier': {
                'new_tab': 'on',
            },
        }
    )
    return officer
