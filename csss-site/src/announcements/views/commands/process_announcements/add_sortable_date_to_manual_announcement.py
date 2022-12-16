import datetime

import pytz
from django.conf import settings

from csss.setup_logger import get_logger


def add_sortable_date_to_manual_announcement(timezone_difference, manual_announcement):
    """
    create the sortable_date for the manual announcement

    Keyword Argument
    manual_announcement -- the manual announcement whose date needs to be made sortable

    Return
    manual_announcement -- a manual announcement with an additional sortable_date property
    """
    logger = get_logger()
    manual_announcement.sortable_date = \
        pytz.timezone(settings.WEBSITE_TIME_ZONE).localize(
            manual_announcement.date + datetime.timedelta(hours=timezone_difference)
        )
    logger.info('[process_announcements return_manual_announcement_with_date)] generated '
                f'date {manual_announcement.sortable_date} from date {manual_announcement.date}')
    return manual_announcement
