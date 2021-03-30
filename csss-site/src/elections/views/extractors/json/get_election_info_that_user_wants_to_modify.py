from elections.models import Nominee, NomineeSpeech, NomineePosition
from elections.views.election_management import NOM_POSITIONS_KEY, NOM_ID_KEY, NOM_SPEECH_KEY, NOM_NAME_KEY, \
    NOM_POSITION_AND_SPEECH_POST_KEY, NOM_EMAIL_KEY, NOM_FACEBOOK_KEY, NOM_LINKEDIN_KEY, NOM_DISCORD_USERNAME_KEY, \
    ELECTION_DATE_KEY, ELECTION_TYPE_KEY, ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, NOM_POSITION_KEY
from elections.views.election_management_helper import _get_existing_election_by_id


def get_information_for_election_user_wants_to_modify_in_json(election_id):
    """
    Returns information about the election

    Keyword Argument
    election_id -- the id for the election to get information about

    Return
    election_dictionary -- a JSON representation of the election information and its list of nominees
    error_messages -- potential error message list
    """
    election = _get_existing_election_by_id(election_id)
    if election is None:
        return {}, ["No valid election found for given election id"]

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
                    NOM_POSITION_AND_SPEECH_POST_KEY: speech_and_position_pairings, NOM_EMAIL_KEY: nominee.email,
                    NOM_LINKEDIN_KEY: nominee.linked_in, NOM_FACEBOOK_KEY: nominee.facebook,
                    NOM_DISCORD_USERNAME_KEY: nominee.discord
                }
            else:
                nominees_dict_to_display[nominee.name][NOM_POSITION_AND_SPEECH_POST_KEY].extend(
                    speech_and_position_pairings
                )
            nominee_names.append(nominee.name)

    election_dictionary = {
        ELECTION_TYPE_KEY: election.election_type, ELECTION_DATE_KEY: election.date.strftime("%Y-%m-%d %H:%M"),
        ELECTION_WEBSURVEY_LINK_KEY: election.websurvey, ELECTION_NOMINEES_KEY: [
            nominee_info for nominee_info in nominees_dict_to_display.values()
        ]
    }

    return election_dictionary, None
