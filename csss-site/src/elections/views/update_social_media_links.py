from django.http import HttpResponseRedirect

from about.models import Officer
from elections.models import Nominee


def update_social_media_links(request):
    officers_dict = {
        officer.full_name: officer.sfu_computing_id
        for officer in Officer.objects.all().exclude(sfu_computing_id="NA").exclude(sfu_computing_id="")
    }
    for nominee in Nominee.objects.all():
        if nominee.full_name in officers_dict:
            nominee.sfuid = officers_dict[nominee.full_name]
            nominee.save()
    return HttpResponseRedirect("/elections/")
