from django.shortcuts import render

from elections.views.ElectionModelConstants import ELECTION_JSON_KEY__ELECTION_TYPE, ELECTION_JSON_KEY__DATE, \
    ELECTION_JSON_VALUE__DATE_AND_TIME_FORMAT, ELECTION_JSON_KEY__WEBSURVEY, ELECTION_JSON_KEY__NOMINEES, \
    ELECTION_JSON_KEY__NOM_NAME, ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS, \
    ELECTION_JSON_KEY__NOM_POSITION_NAMES, ELECTION_JSON_KEY__NOM_SPEECH, ELECTION_JSON_KEY__NOM_FACEBOOK, \
    ELECTION_JSON_KEY__NOM_LINKEDIN, ELECTION_JSON_KEY__NOM_EMAIL, ELECTION_JSON_KEY__NOM_DISCORD
from elections.views.create_context.json.create_json_context import \
    create_json_election_context_from_user_inputted_election_dict


def display_empty_election_json(request, context):
    """
    creates the dictionary that the user has to fill in to create an election

    Keyword Argument
    request -- the django request object
    context -- the context dictionary that needs to have the election dictionary template inserted into it

    Return
    takes user to the page where they are asked to fill in the JSON for the new election
    """
    election = {
            ELECTION_JSON_KEY__ELECTION_TYPE: "",
            ELECTION_JSON_KEY__DATE: ELECTION_JSON_VALUE__DATE_AND_TIME_FORMAT,
            ELECTION_JSON_KEY__WEBSURVEY: "",
            ELECTION_JSON_KEY__NOMINEES: [
                {
                    ELECTION_JSON_KEY__NOM_NAME: "",
                    ELECTION_JSON_KEY__NOM_POSITION_AND_SPEECH_PAIRINGS: [
                        {ELECTION_JSON_KEY__NOM_POSITION_NAMES: [], ELECTION_JSON_KEY__NOM_SPEECH: "NONE"}],
                    ELECTION_JSON_KEY__NOM_FACEBOOK: "NONE", ELECTION_JSON_KEY__NOM_LINKEDIN: "NONE",
                    ELECTION_JSON_KEY__NOM_EMAIL: "NONE",
                    ELECTION_JSON_KEY__NOM_DISCORD: "NONE"
                }
            ]
    }
    context.update(create_json_election_context_from_user_inputted_election_dict(election_information=election))
    return render(request, 'elections/create_election/create_election_json.html', context)
