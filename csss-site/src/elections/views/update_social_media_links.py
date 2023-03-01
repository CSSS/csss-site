from django.http import HttpResponseRedirect

from elections.models import Nominee


def update_social_media_links(request):
    nominees = Nominee.objects.all().order_by('full_name')
    no_entry_options = ["NA", "NONE"]
    for nominee in nominees:
        if nominee.discord_username in no_entry_options:
            nominee.discord_username = None
        if nominee.discord in no_entry_options:
            nominee.discord = None
        else:
            if nominee.discord_username is None:
                nominee.discord_username = nominee.discord
        if nominee.discord_nickname in no_entry_options:
            nominee.discord_nickname = None
        if nominee.instagram in no_entry_options:
            nominee.instagram = None
        if nominee.discord_id in no_entry_options:
            nominee.discord_id = None
        if nominee.email in no_entry_options:
            nominee.email = None
        if nominee.facebook in no_entry_options:
            nominee.facebook = None
        if nominee.linkedin in no_entry_options:
            nominee.linkedin = None
        nominee.save()
        print(nominee)
    return HttpResponseRedirect("/elections/")
