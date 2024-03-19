from django.conf import settings

from csss.views.send_discord_group_message import send_discord_group_message


def send_notification_for_saved_election_results(election_obj):
    """
    Send notification to the exec chat to alert the execs of the new election voting results
    """
    url = f'http://{settings.HOST_ADDRESS}'
    if settings.DEBUG:
        url += f":{settings.PORT}"
    url += "/elections/"
    send_discord_group_message(
        573280123285929994, "New Election Results Detected",
        (
            f"Results saved for election {election_obj.human_friendly_name}\n"
            f"[Graph for Election {election_obj.human_friendly_name}]({url}{election_obj.slug}/graphs)\n"
            f"[Graph for All Elections ]({url}graphs)\n"
        )
    )
