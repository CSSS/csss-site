import json

from django.shortcuts import render

from elections.views.Constants import JSON_INPUT_FIELD_KEY, ELECTION_DATE_KEY, ELECTION_TYPE_KEY, \
    ELECTION_WEBSURVEY_LINK_KEY, ELECTION_NOMINEES_KEY, NOM_NAME_KEY, NOM_POSITION_AND_SPEECH_KEY, NOM_FACEBOOK_KEY, \
    NOM_DISCORD_USERNAME_KEY, NOM_POSITIONS_KEY, NOM_LINKEDIN_KEY, NOM_SPEECH_KEY, NOM_EMAIL_KEY


def display_empty_election_json(request, context):
    """
    creates the dictionary that the user has to fill in to create an election

    Keyword Argument
    request -- the django request object
    context -- the context dictionary that needs to have the election dictionary template inserted into it

    Return
    takes user to the page where they are asked to fill in the JSON for the new election
    """
    context[JSON_INPUT_FIELD_KEY] = json.dumps(
        {
            ELECTION_TYPE_KEY: "", ELECTION_DATE_KEY: "YYYY-MM-DD HH:MM",
            ELECTION_WEBSURVEY_LINK_KEY: "",
            ELECTION_NOMINEES_KEY: [
                {
                    NOM_NAME_KEY: "",
                    NOM_POSITION_AND_SPEECH_KEY: [{NOM_POSITIONS_KEY: [], NOM_SPEECH_KEY: "NONE"}],
                    NOM_FACEBOOK_KEY: "NONE", NOM_LINKEDIN_KEY: "NONE", NOM_EMAIL_KEY: "NONE",
                    NOM_DISCORD_USERNAME_KEY: "NONE"
                }
            ]
        }
    )
    return render(request, 'elections/create_election/create_election_json.html', context)
