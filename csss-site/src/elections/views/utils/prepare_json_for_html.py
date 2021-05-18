import json


def prepare_json_for_html(input_json):
    """
    puts the json through the following process

    json.dumps(input_json).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
    """
    return json.dumps(input_json).replace("\\r", "").replace("\\n", "").replace("\\t", "").replace("\\", "")
