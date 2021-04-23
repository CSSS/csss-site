from elections.models import Election, Nominee, NomineePosition, NomineeSpeech

TAB_STRING = 'elections'

# context keys used in csss-site/src/elections/templates/elections/election_page.html
INPUT_ELECTION_ID__VALUE = 'input_election_id__value'
ELECTION__HTML_NAME = 'election__html_name'
NOMINEES_HTML__NAME = 'nominees__html_name'
ELECTION_MANAGEMENT_PERMISSION = 'election_management_permission'
BUTTON_MODIFY_ELECTION_ID__NAME = 'button_modify_election_id__name'
INPUT_ELECTION_ID__NAME = 'input_election_id__name'
ELECTION_ID = 'election_id'


# context keys used in csss-site/src/elections/templates/elections/create_election/submission_buttons.html
INPUT_REDIRECT_ELECTION__NAME = 'input_redirect_election_submit__name'
INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE = (
    'input_redirect_election_submit_and_continue_editing__value'
)
INPUT_REDIRECT_ELECTION_SUBMIT__VALUE = 'input_redirect_election_submit__value'
CREATE_NEW_JSON_ELECTION__NAME = 'create_election'
SAVE_NEW_JSON_ELECTION__VALUE = 'Save Election'
SAVE_AND_CONTINUE_EDITING_NEW_JSON_ELECTION__VALUE = 'Save and Continue Editing Election'

# context keys used in csss-site/src/elections/templates/elections/create_election/submission_buttons.html
# csss-site/src/elections/templates/elections/json/json_beautify.html
SAVE_NEW_JSON_ELECTION__BUTTON_ID = 'save_election__button_id'
SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE = 'save_election_button'
SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID = 'save_new_election_and_continue_editing__button_id'
SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE = 'save_new_election_and_continue_editing__button'


# context keys used in csss-site/src/elections/templates/elections/json/json_instructions.html
TYPES_OF_ELECTIONS = 'types_of_elections'
VALID_POSITION_NAMES = 'valid_position_names'

# csss-site/src/elections/templates/elections/json/js_formatting_script.html
ELECTION_JSON__KEY = 'election'

# csss-site/src/elections/templates/elections/json/creating_election_errors.html
# csss-site/src/elections/templates/elections/json/json_beautify.html
FORMAT_ELECTION_JSON__DIV_ID_NAME = 'json_formatting_div__name'
JS_FORMATTING_ERROR = 'js_formatting_error'

# csss-site/src/elections/templates/elections/json/input_election.html
# csss-site/src/elections/templates/elections/json/json_beautify.html
USER_INPUTTED_ELECTION_JSON__KEY = 'election_input__html_name'
USER_INPUTTED_ELECTION_JSON = 'election_input'


# keys/values in Election JSON
ELECTION_JSON_KEY__ELECTION_TYPE = Election.election_type.field_name
ELECTION_JSON_KEY__DATE = Election.date.field_name
ELECTION_JSON_VALUE__DATE_AND_TIME_FORMAT = "YYYY-MM-DD HH:MM"
ELECTION_JSON_KEY__WEBSURVEY = Election.websurvey.field_name
ELECTION_JSON_KEY__NOMINEES = Nominee.__name__.lower()+"s"
ELECTION_JSON_KEY__NOM_NAME = Nominee.name.field_name
ELECTION_JSON_KEY__NOM_POSITION_NAMES = NomineePosition.position_name.field_name + "s"
ELECTION_JSON_KEY__NOM_SPEECH = NomineeSpeech.speech.field_name
ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS = \
    f'{ELECTION_JSON_KEY__NOM_POSITION_NAMES}_and_{ELECTION_JSON_KEY__NOM_SPEECH}_pairings'
ELECTION_JSON_KEY__NOM_FACEBOOK = Nominee.facebook.field_name
ELECTION_JSON_KEY__NOM_LINKEDIN = Nominee.linkedin.field_name
ELECTION_JSON_KEY__NOM_EMAIL = Nominee.email.field_name
ELECTION_JSON_KEY__NOM_DISCORD = Nominee.discord.field_name
