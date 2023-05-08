import json

from csss.setup_logger import Loggers
from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import ID_KEY
from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_POSITION_NAME, ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_NAME, \
    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_INSTAGRAM, \
    ELECTION_JSON_KEY__NOM_DISCORD_ID, ELECTION_JSON_KEY__NOM_SFUID


def get_election_nominees(election):
    """
    Get the nominees for a specified election

    Keyword Argument
    election -- the election obj whose nominees the function returns

    Return
    nominees_dict_to_display -- the list of nominees for a specified election in the following format
    {
        [
            'id' : 'nominee.id' ,
            'name' : 'nominee.full_name' ,
            'position_names_and_speech_pairings' : {
                [
                    {
                        'id' : 'speech.id' ,
                        'speech' : 'speech.speech' ,
                        'position_names' : {
                            'id' : 'position_name.id' ,
                            'position_name' : 'position_name.position_name'
                        }
                    }
                ]
            }
        ]
    }
    """
    logger = Loggers.get_logger()
    nominees = [
        nominee for nominee in Nominee.objects.all().filter(
            election=election
        ).order_by('nomineespeech__nomineeposition__position_index',
                   'id')
    ]
    nominees_dict_to_display = {}
    nominee_names = []
    for nominee in nominees:
        if nominee.full_name not in nominee_names:
            speech_and_position_pairings = []
            speech_ids = []
            for speech in NomineeSpeech.objects.all().filter(nominee=nominee).order_by(
                'nomineeposition__position_index'
            ):
                speech_and_position_pairing = {}
                if speech.id not in speech_ids:
                    speech_ids.append(speech.id)
                    for position_name in NomineePosition.objects.all().filter(nominee_speech=speech).order_by(
                        'position_index'
                    ):
                        if ELECTION_JSON_KEY__NOM_POSITION_NAMES not in speech_and_position_pairing:
                            speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES] = [{
                                ID_KEY: position_name.id,
                                ELECTION_JSON_KEY__NOM_POSITION_NAME: position_name.position_name
                            }]
                        else:
                            speech_and_position_pairing[ELECTION_JSON_KEY__NOM_POSITION_NAMES].append(
                                {
                                    ID_KEY: position_name.id,
                                    ELECTION_JSON_KEY__NOM_POSITION_NAME: position_name.position_name
                                }
                            )
                    speech_and_position_pairing[ID_KEY] = speech.id
                    speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH] = speech.formatted_speech
                    if speech_and_position_pairing is not None:
                        speech_and_position_pairings.append(speech_and_position_pairing)

            if nominee.full_name not in nominees_dict_to_display:
                nominees_dict_to_display[nominee.full_name] = {
                    ID_KEY: nominee.id,
                    ELECTION_JSON_KEY__NOM_NAME: nominee.get_full_name,
                    ELECTION_JSON_KEY__NOM_SFUID: nominee.get_sfuid,
                    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS: speech_and_position_pairings,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee.get_facebook,
                    ELECTION_JSON_KEY__NOM_INSTAGRAM: nominee.get_instagram,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee.get_linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee.get_email,
                    ELECTION_JSON_KEY__NOM_DISCORD_ID: nominee.get_discord_id
                }
            else:
                nominees_dict_to_display[nominee.full_name][
                    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS
                ].extend(speech_and_position_pairings)
            nominee_names.append(nominee.full_name)
    nominees = [nominee_info for nominee_info in nominees_dict_to_display.values()]
    logger.info("[elections/get_election_nominees.py get_election_nominees()] nominees=")
    logger.info(json.dumps(nominees, indent=3))
    return nominees
