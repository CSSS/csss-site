import re

import requests
from django.conf import settings


def create_github_issue(error_messages):
    """
    Files a css-site error as an issue under the repo

    :param error_messages: the error stack trace to include in the body of the github issue
    :return:
    """
    last_message = None
    last_line = len(error_messages)-1
    while last_line > -1:
        if error_messages[last_line] != "\n":
            last_message = error_messages[last_line]
            last_line = -1
        else:
            last_line -= 1
    beginning_of_error_message = re.match(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} = ERROR = ", last_message
    )
    beginning_of_error_message = beginning_of_error_message.regs[0][1] if beginning_of_error_message else 0
    last_message = last_message[beginning_of_error_message:]
    requests.post(
        url="https://api.github.com/repos/csss/csss-site/issues",
        headers={
            "Accept": "application/vnd.github+json",

            "Authorization": f"Bearer {settings.GITHUB_ACCESS_TOKEN}"
        },
        json={
            "title": last_message,
            "body": "```\n" + "".join(error_messages) + "\n```"
        }
    )
