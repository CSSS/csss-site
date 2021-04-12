from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.Constants import NOM_POSITIONS_KEY, NOM_ID_KEY, NOM_POSITION_KEY, NOM_SPEECH_KEY, \
    NOM_NAME_KEY, NOM_POSITION_AND_SPEECH_KEY, NOM_EMAIL_KEY, NOM_LINKEDIN_KEY, NOM_FACEBOOK_KEY, \
    NOM_DISCORD_USERNAME_KEY


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
            for speech in NomineeSpeech.objects.all().filter(nominee=nominee):
                speech_and_position_pairing = {}
                for position_name in NomineePosition.objects.all().filter(nominee_speech=speech):
                    if NOM_POSITIONS_KEY not in speech_and_position_pairing:
                        speech_and_position_pairing[NOM_POSITIONS_KEY] = [{
                            NOM_ID_KEY: position_name.id,
                            NOM_POSITION_KEY: position_name.position_name
                        }]
                    else:
                        speech_and_position_pairing[NOM_POSITIONS_KEY].append(
                            {
                                NOM_ID_KEY: position_name.id,
                                NOM_POSITION_KEY: position_name.position_name
                            }
                        )
                speech_and_position_pairing[NOM_ID_KEY] = speech.id
                speech_and_position_pairing[NOM_SPEECH_KEY] = speech.speech
                if speech_and_position_pairing is not None:
                    speech_and_position_pairings.append(speech_and_position_pairing)

            if nominee.name not in nominees_dict_to_display:
                nominees_dict_to_display[nominee.name] = {
                    NOM_ID_KEY: nominee.id, NOM_NAME_KEY: nominee.name,
                    NOM_POSITION_AND_SPEECH_KEY: speech_and_position_pairings, NOM_EMAIL_KEY: nominee.email,
                    NOM_LINKEDIN_KEY: nominee.linked_in, NOM_FACEBOOK_KEY: nominee.facebook,
                    NOM_DISCORD_USERNAME_KEY: nominee.discord
                }
            else:
                nominees_dict_to_display[nominee.name][NOM_POSITION_AND_SPEECH_KEY].extend(
                    speech_and_position_pairings
                )
            nominee_names.append(nominee.name)
    return [nominee_info for nominee_info in nominees_dict_to_display.values()]
