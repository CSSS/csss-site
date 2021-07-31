import json
import logging

from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_FACEBOOK, ELECTION_JSON_KEY__NOM_LINKEDIN, \
    ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD, ELECTION_JSON_KEY__NOM_POSITION_NAMES, \
    ELECTION_JSON_KEY__NOM_POSITION_NAME, ELECTION_JSON_KEY__NOM_SPEECH, ID_KEY

logger = logging.getLogger('csss_site')


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
            'name' : 'nominee.name' ,
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
    nominees = [
        nominee for nominee in Nominee.objects.all().filter(
            election=election
        ).order_by('nomineespeech__nomineeposition__position_index',
                   'id')
    ]
    nominees_dict_to_display = {}
    nominee_names = []
    for nominee in nominees:
        if nominee.name not in nominee_names:
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
                    speech_and_position_pairing[ELECTION_JSON_KEY__NOM_SPEECH] = speech.speech
                    if speech_and_position_pairing is not None:
                        speech_and_position_pairings.append(speech_and_position_pairing)

            if nominee.name not in nominees_dict_to_display:
                nominees_dict_to_display[nominee.name] = {
                    ID_KEY: nominee.id,
                    ELECTION_JSON_KEY__NOM_NAME: nominee.name,
                    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS: speech_and_position_pairings,
                    ELECTION_JSON_KEY__NOM_FACEBOOK: nominee.facebook,
                    ELECTION_JSON_KEY__NOM_LINKEDIN: nominee.linkedin,
                    ELECTION_JSON_KEY__NOM_EMAIL: nominee.email,
                    ELECTION_JSON_KEY__NOM_DISCORD: nominee.discord
                }
            else:
                nominees_dict_to_display[nominee.name][ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS].extend(
                    speech_and_position_pairings
                )
            nominee_names.append(nominee.name)
    nominees = [nominee_info for nominee_info in nominees_dict_to_display.values()]
    logger.info("[elections/get_election_nominees.py get_election_nominees()] nominees=")
    logger.info(json.dumps(nominees, indent=3))
    return nominees
