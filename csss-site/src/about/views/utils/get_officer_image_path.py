import logging
import os

from django.conf import settings

from about.views.utils.get_term_season_number import get_term_season_number

logger = logging.getLogger('csss_site')


def get_officer_image_path(term_obj, full_name):
    """
    determines what the image path for the officer should be

    Keyword Argument
    term_obj -- the term for the officer
    full_name -- the officer's full name

    Return
    pic_path -- the path for the officer's image
    """
    valid_picture_extensions = ['jpg', 'jpeg', 'png']
    valid_picture_path = None
    if settings.ENVIRONMENT == "LOCALHOST":
        path_prefix = "about_static/"
        stock_photo_path = f"{path_prefix}stockPhoto.jpg"
        officer_photo_path = f'{path_prefix}exec-photos/'
        for valid_picture_extension in valid_picture_extensions:
            if valid_picture_path is None or valid_picture_path == stock_photo_path:
                term_season_number = _get_term_obj_season_number(term_obj)
                if term_season_number is None:
                    valid_picture_path = stock_photo_path
                else:
                    pic_path = (f'{officer_photo_path}{term_obj.year}_0{term_season_number}_'
                                f'{term_obj.term}/{full_name.replace(" ", "_")}.{valid_picture_extension}')
                    full_path = settings.BASE_DIR + '/csss-site/src/about/static/' + pic_path
                    logger.info("[about/officer_management_helper.py get_officer_image_path()] "
                                f"full_path = {full_path}")
                    if full_path is None or not os.path.isfile(full_path):
                        valid_picture_path = stock_photo_path
                    else:
                        valid_picture_path = pic_path
    else:
        path_prefix = "about_static/"
        stock_photo_path = f"{path_prefix}stockPhoto.jpg"
        officer_photo_path = f'{path_prefix}exec-photos/'
        logger.info(f"[about/officer_management_helper.py get_officer_image_path()] "
                    f"path_prefix = {path_prefix}")
        for valid_picture_extension in valid_picture_extensions:
            if valid_picture_path is None or valid_picture_path == stock_photo_path:
                term_season_number = _get_term_obj_season_number(term_obj)
                if term_season_number is None:
                    valid_picture_path = stock_photo_path
                else:
                    pic_path = (f'{term_obj.year}_0{_get_term_obj_season_number(term_obj)}_'
                                f'{term_obj.term}/{full_name.replace(" ", "_")}.{valid_picture_extension}')
                    pic_path = f"{officer_photo_path}{pic_path}"
                    logger.info(f"[about/officer_management_helper.py get_officer_image_path()] "
                                f"officer.image = {pic_path}")
                    absolute_path = f"{settings.STATIC_ROOT}{pic_path}"
                    logger.info(f"[about/officer_management_helper.py get_officer_image_path()] "
                                f"absolute_path = {absolute_path}")
                    if not os.path.isfile(absolute_path):
                        valid_picture_path = stock_photo_path
                    else:
                        valid_picture_path = pic_path
    logger.info("[about/officer_management_helper.py get_officer_image_path()] "
                f"image set to = '{valid_picture_path}'")
    return valid_picture_path


def _get_term_obj_season_number(term_obj):
    """
    Gets the term number using the term object

    Keyword Arguments
    term -- the term object that the function will return its number

    Returns
    term_season_number -- the number of the tem, e.g. 1, 2, or 3. this can also be -1 if the
        term does not have a valid season
    """
    return get_term_season_number(term_obj.term)
