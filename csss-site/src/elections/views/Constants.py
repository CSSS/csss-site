from elections.models import Election, Nominee, NomineePosition, NomineeSpeech

TAB_STRING = 'elections'

ID_KEY = 'id'

ELECTION__HTML_NAME = 'election__html_name'
ELECTION_MANAGEMENT_PERMISSION = 'election_management_permission'
BUTTON_MODIFY_ELECTION_ID__NAME = 'button_modify_election_id__name'
ELECTION_ID = 'election_id'

INPUT_ELECTION_ID__NAME = 'input_election_id__name'
INPUT_ELECTION_ID__VALUE = 'input_election_id__value'

NOMINEES_HTML__NAME = 'nominees__html_name'

INPUT_REDIRECT_ELECTION__NAME = 'input_redirect_election_submit__name'
INPUT_REDIRECT_ELECTION_SUBMIT_AND_CONTINUE_EDITING__VALUE = (
    'input_redirect_election_submit_and_continue_editing__value'
)
INPUT_REDIRECT_ELECTION_SUBMIT__VALUE = 'input_redirect_election_submit__value'
CREATE_NEW_ELECTION__NAME = 'create_election'
UPDATE_EXISTING_ELECTION__NAME = 'update_election'
SAVE_ELECTION__VALUE = 'Save Election'
SAVE_AND_CONTINUE_EDITING_ELECTION__VALUE = 'Save and Continue Editing Election'

SAVE_NEW_JSON_ELECTION__BUTTON_ID = 'save_election__button_id'
SAVE_NEW_JSON_ELECTION__BUTTON_ID_VALUE = 'save_election_button'
SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID = 'save_new_election_and_continue_editing__button_id'
SAVE_NEW_JSON_ELECTION_AND_CONTINUE_EDITING__BUTTON_ID_VALUE = 'save_new_election_and_continue_editing__button'

TYPES_OF_ELECTIONS = 'types_of_elections'
VALID_POSITION_NAMES = 'valid_position_names'

ELECTION_JSON__KEY = 'election'

FORMAT_ELECTION_JSON__DIV_ID_NAME = 'json_formatting_div__name'
JS_FORMATTING_ERROR = 'js_formatting_error'

USER_INPUTTED_ELECTION_JSON__KEY = 'election_input__html_name'
USER_INPUTTED_ELECTION_JSON = 'election_input'

# keys/values in Election JSON
ELECTION_JSON_KEY__ELECTION_TYPE = Election.election_type.field_name
ELECTION_JSON_KEY__DATE = Election.date.field_name
ELECTION_JSON_WEBFORM_KEY__TIME = "time"
ELECTION_JSON_VALUE__DATE_AND_TIME_FORMAT = "YYYY-MM-DD HH:MM"
ELECTION_JSON_KEY__WEBSURVEY = Election.websurvey.field_name
ELECTION_JSON_KEY__NOMINEES = Nominee.__name__.lower() + "s"
ELECTION_JSON_KEY__NOM_NAME = Nominee.name.field_name
ELECTION_JSON_KEY__NOM_POSITION_NAMES = NomineePosition.position_name.field_name + "s"
ELECTION_JSON_KEY__NOM_POSITION_NAME = NomineePosition.position_name.field_name
ELECTION_JSON_KEY__NOM_SPEECH = NomineeSpeech.speech.field_name
ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS = \
    f'{ELECTION_JSON_KEY__NOM_POSITION_NAMES}_and_{ELECTION_JSON_KEY__NOM_SPEECH}_pairings'
ELECTION_JSON_KEY__NOM_FACEBOOK = Nominee.facebook.field_name
ELECTION_JSON_KEY__NOM_LINKEDIN = Nominee.linkedin.field_name
ELECTION_JSON_KEY__NOM_EMAIL = Nominee.email.field_name
ELECTION_JSON_KEY__NOM_DISCORD = Nominee.discord.field_name

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'
DATE_AND_TIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

INPUT_DATE__NAME = 'input_date__name'
INPUT_DATE__VALUE = 'input_date__value'
INPUT_TIME__NAME = 'input_time__name'
INPUT_TIME__VALUE = 'input_time__value'
POSITIONS_KEY = 'positions'
SELECT_ELECTION_TYPE__NAME = 'select_election_type__name'
SELECTED_ELECTION_TYPE = 'selected_election_type'
CURRENT_ELECTION_TYPES = 'election_types'
SELECTED_ELECTION_TYPE__HTML_NAME = 'selected_election_type__html_name'
INPUT_WEBSURVEY__NAME = 'input_websurvey__name'

CURRENT_WEBSURVEY_LINK = 'current_websurvey_link'
INPUT_NOMINEE_ID__NAME = 'input_nominee_id__name'

CREATE_NEW_ELECTION__HTML_NAME = 'create_new_election__html_name'

NOMINEE_DIV__NAME = 'nominee_div__name'

INPUT_NOMINEE_SPEECH__NAME = 'input_nominee_speech__name'

INPUT_NOMINEE_SPEECH_AND_POSITION_PAIRING__NAME = 'input_nominee_speech_and_position_pairing__name'
INPUT_NOMINEE_POSITION_NAMES__NAME = 'input_nominee_position_names__name'

INPUT_SPEECH_ID__NAME = 'input_speech_id__name'

INPUT_NOMINEE_NAME__NAME = 'input_nominee_name__name'

INPUT_NOMINEE_FACEBOOK__NAME = 'input_nominee_facebook__name'
INPUT_NOMINEE_LINKEDIN__NAME = 'input_nominee_linkedin__name'
INPUT_NOMINEE_EMAIL__NAME = 'input_nominee_email__name'
INPUT_NOMINEE_DISCORD__NAME = 'input_nominee_discord__name'

CURRENT_OFFICER_POSITIONS = 'current_officer_positions'

ENDPOINT_MODIFY_VIA_JSON = 'election_modification_json'
ENDPOINT_MODIFY_VIA_WEBFORM = 'election_modification_webform'

NOMINEE_NAMES__HTML_NAME = 'nominee_names__html_name'
NEW_NOMINEE_NAMES_FOR_NOMINEE_LINKS = 'new_nominee_names'
NOMINEE_NAMES__VALUE = 'nominee_names__value'
NEW_ELECTION = 'new_election'

CURRENT_ELECTION = 'current_election'

DRAFT_NOMINEE_LINKS = 'draft_nominee_links'

SAVED_NOMINEE_LINKS__HTML_NAME = 'saved_nominee_links__html_name'
SAVED_NOMINEE_LINKS = 'saved_nominee_links'

DELETE__HTML_NAME = 'delete__html_name'
DELETE = 'delete'

SAVED_NOMINEE_LINK__ID__HTML_NAME = 'saved_nominee_link__id__html_name'
SAVED_NOMINEE_LINK__ID = 'saved_nominee_link__id'

SAVED_NOMINEE_LINK__NAME__HTML_NAME = 'saved_nominee_link__name__html_name'
SAVED_NOMINEE_LINK__NAME = 'saved_nominee_link__name'

SAVED_NOMINEE_LINK__NOMINEE__HTML_NAME = 'saved_nominee_link__nominee__html_name'
SAVED_NOMINEE_LINK__NOMINEE = 'saved_nominee_link__nominee'

NO_NOMINEE_LINKED__HTML_NAME = 'no_nominee_linked__html_name'
NO_NOMINEE_LINKED = 'no_nominee_linked'

NOMINEE_LINK_ID__HTML_NAME = 'nominee_link_id__html_name'
NOMINEE_LINK_ID = 'nominee_link_id'

NOMINEE_LINKS = 'nominee_links'

CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINKS__HTML_NAME = 'create_or_update_nominee_via_nominee_link__html_name'
ENDPOINT_CREATE_OR_UPDATE_NOMINEE_VIA_NOMINEE_LINK = 'create_or_update_via_nominee_links'
