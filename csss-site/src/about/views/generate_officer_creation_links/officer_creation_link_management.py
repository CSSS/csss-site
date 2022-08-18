import logging

logger = logging.getLogger('csss_site')

# used on show_create_link_for_officer_page
HTML_TERM_KEY = 'term'
HTML_YEAR_KEY = 'year'
HTML_DATE_KEY = 'date'
HTML_POSITION_KEY = 'positions'
HTML_OVERWRITE_KEY = 'overwrite'
HTML_NEW_START_DATE_KEY = 'new_start_date'

# the key used to indicate passphrase in link given to the new officers
HTML_PASSPHRASE_GET_KEY = HTML_PASSPHRASE_POST_KEY = HTML_REQUEST_SESSION_PASSPHRASE_KEY = \
    HTML_PASSPHRASE_SESSION_KEY = 'passphrase'

# used on show_generated_officer_links
HTML_OFFICER_CREATION_LINKS_KEY = 'officer_creation_links'

# used on add_officer page
HTML_VALUE_ATTRIBUTE_FOR_TERM = 'term_value'
HTML_VALUE_ATTRIBUTE_FOR_YEAR = 'year_value'
HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION = 'term_position_value'
HTML_TERM_POSITION_KEY = 'term_position'
HTML_VALUE_ATTRIBUTE_FOR_TERM_POSITION_NUMBER = 'term_position_number_value'
HTML_TERM_POSITION_NUMBER_KEY = 'position_index'
HTML_VALUE_ATTRIBUTE_FOR_OFFICER_EMAIL_CONTACT = 'sfu_email_list_address_value'
HTML_OFFICER_EMAIL_CONTACT_KEY = 'sfu_email_list_address'
HTML_VALUE_ATTRIBUTE_FOR_NAME = 'name_value'
HTML_NAME_KEY = 'name'
HTML_VALUE_ATTRIBUTE_FOR_SFUID = 'sfuid_value'
HTML_SFUID_KEY = 'sfu_computing_id'
HTML_VALUE_ATTRIBUTE_FOR_SFUID_EMAIL_ALIAS = 'sfuid_email_alias_value'
HTML_SFUID_EMAIL_ALIAS_KEY = 'sfuid_email_alias'
HTML_VALUE_ATTRIBUTE_FOR_EMAIL = 'email_value'
HTML_EMAIL_KEY = 'email'
HTML_VALUE_ATTRIBUTE_FOR_GMAIL = 'gmail_value'
HTML_GMAIL_KEY = 'gmail'
HTML_VALUE_ATTRIBUTE_FOR_PHONE_NUMBER = 'phone_number_value'
HTML_PHONE_NUMBER_KEY = 'phone_number'
HTML_VALUE_ATTRIBUTE_FOR_GITHUB_USERNAME = 'github_username_value'
HTML_GITHUB_USERNAME_KEY = 'github_username'
HTML_VALUE_ATTRIBUTE_FOR_COURSE1 = 'course1_value'
HTML_COURSE1_KEY = 'course1'
HTML_VALUE_ATTRIBUTE_FOR_COURSE2 = 'course2_value'
HTML_COURSE2_KEY = 'course2'
HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE1 = 'language1_value'
HTML_LANGUAGE1_KEY = 'language1'
HTML_VALUE_ATTRIBUTE_FOR_LANGUAGE2 = 'language2_value'
HTML_LANGUAGE2_KEY = 'language2'
HTML_VALUE_ATTRIBUTE_FOR_BIO = 'bio_value'
HTML_BIO_KEY = 'bio'

# used on allow_officer_to_choose_name page
HTML_PAST_OFFICERS_KEY = 'past_officers'

HTML_VALUE_ATTRIBUTE_FOR_TIME = "time_value"

PASSPHRASE_ERROR_KEY = 'passphrase_error'
REQUEST_SESSION_USER_INPUT_ERROR_KEY = 'user_input_error'

YEAR_LONG_OFFICER_POSITIONS_START_IN_SPRING = ["Frosh Week Chair"]
YEAR_LONG_OFFICER_POSITION_START_IN_SUMMER = [
    "President", "Vice-President", "Treasurer", "Director of Resources", "Director of Events",
    "Assistant Director of Events", "Director of Communications", "Director of Archives",
    "SFSS Council Representative"
]
TWO_TERM_POSITIONS_START_IN_FALL = [
    "First Year Representative 1", "First Year Representative 2"
]