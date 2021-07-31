import datetime

import django
from django.forms import model_to_dict

from about.models import OfficerEmailListAndPositionMapping
from elections.models import NomineeLink, NomineeSpeech, Election


def make_context_value_json_serializable(context_value):
    if type(context_value) is list and len(context_value) == 0:
        return []
    if type(context_value) is list and len(context_value) > 0:
        if type(context_value[0]) is NomineeLink or type(context_value[0]) is NomineeSpeech or type(
                context_value[0]) is OfficerEmailListAndPositionMapping:
            return [_convert_model_to_dict(model_to_dict(model_instance).items()) for model_instance in context_value]
    if type(context_value) is django.db.models.query.QuerySet:
        return [_convert_model_to_dict(model_to_dict(model_instance).items()) for model_instance in context_value]
    if type(context_value) is Election:
        return _convert_model_to_dict(model_to_dict(context_value).items())
    return _make_value_json_serializable(context_value)


def _convert_model_to_dict(model_attributes):
    return {key: _make_value_json_serializable(value) for (key, value) in model_attributes}


def _make_value_json_serializable(value):
    return value.strftime('%Y-%m-%d') if type(value) is datetime.datetime else value