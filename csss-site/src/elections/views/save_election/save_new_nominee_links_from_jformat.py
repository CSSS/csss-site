from about.views.input_new_officers.enter_new_officer_info.utils.get_sfu_info import get_sfu_info
from elections.models import NomineeLink
from elections.views.Constants import NA_STRING


def save_new_nominee_links_from_jformat(election, new_nominee_sfuids_and_discord_ids):
    """
    save new nominee links

    Keyword Arguments
    election -- the election object to save the new nominee links to
    new_nominee_sfuids_and_discord_ids -- the SFU IDs and Discord IDs of the nominees
     that links have to be created for
    """
    if new_nominee_sfuids_and_discord_ids is not None and type(new_nominee_sfuids_and_discord_ids) == str:
        for new_nominee_sfuids_and_discord_id in new_nominee_sfuids_and_discord_ids.split("\r\n"):
            if new_nominee_sfuids_and_discord_id.strip() != "":
                new_nominee_sfuid = new_nominee_sfuids_and_discord_id.split(",")[0].strip()
                new_nominee_discord_id = new_nominee_sfuids_and_discord_id.split(",")[1].strip()
                success, error_message, sfu_info = get_sfu_info(new_nominee_sfuid)
                full_name = f"{sfu_info['firstnames']} {sfu_info['lastname']}" if success else NA_STRING
                nominee_link = NomineeLink(
                    election=election, sfuid=new_nominee_sfuid, discord_id=new_nominee_discord_id,
                    full_name=full_name
                )
                nominee_link.save()
                nominee_link.send_dm()
