import logging

from django.http import HttpResponseRedirect

from about.models import NewOfficer, Officer
from csss.views.determine_user_role import user_is_current_webmaster_or_doa

logger = logging.getLogger('csss_site')


def delete_new_office_links(request):
    """
    Shows the page where the user can select the year, term and positions for whom to create the generation links
    """
    logger.info(f"[about/specify_new_officers.py specify_new_officers()] "
                f"request.POST={request.POST}")
    user_is_current_webmaster_or_doa(request, officers=Officer.objects.all().order_by('-start_date'))
    NewOfficer.objects.all().delete()
    return HttpResponseRedirect("/about/specify_new_officers")
