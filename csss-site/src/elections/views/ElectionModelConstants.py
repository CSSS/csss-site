from elections.models import Election, Nominee, NomineePosition, NomineeSpeech

# keys/values in Election JSON
ELECTION_JSON_KEY__ELECTION_TYPE = Election.election_type.field_name
ELECTION_JSON_KEY__DATE = Election.date.field_name
ELECTION_JSON_WEBFORM_KEY__TIME = "time"
ELECTION_JSON_VALUE__DATE_AND_TIME_FORMAT = "YYYY-MM-DD HH:MM"
ELECTION_JSON_KEY__WEBSURVEY = Election.websurvey.field_name
ELECTION_JSON_KEY__NOMINEES = Nominee.__name__.lower() + "s"
ELECTION_JSON_KEY__NOMINEE = Nominee.__name__.lower()
ELECTION_JSON_KEY__NOM_NAME = Nominee.full_name.field_name
ELECTION_JSON_KEY__NOM_POSITION_NAMES = NomineePosition.position_name.field_name + "s"
ELECTION_JSON_KEY__NOM_POSITION_NAME = NomineePosition.position_name.field_name
ELECTION_JSON_KEY__NOM_SPEECH = NomineeSpeech.speech.field_name
ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS = \
    f'{ELECTION_JSON_KEY__NOM_POSITION_NAMES}_and_{ELECTION_JSON_KEY__NOM_SPEECH}_pairings'
ELECTION_JSON_KEY__NOM_FACEBOOK = Nominee.facebook.field_name
ELECTION_JSON_KEY__NOM_INSTAGRAM = Nominee.instagram.field_name
ELECTION_JSON_KEY__NOM_LINKEDIN = Nominee.linkedin.field_name
ELECTION_JSON_KEY__NOM_EMAIL = Nominee.email.field_name
ELECTION_JSON_KEY__NOM_DISCORD = Nominee.discord.field_name
