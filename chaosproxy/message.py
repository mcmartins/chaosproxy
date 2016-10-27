import json


def format(obj):
    """
    Utility method to format json strings, if is not a json string it returns the original object
    :param obj: the object to format
    :return: the formatted string if json, otherwise the same object
    """
    if not obj:
        obj = ''
    try:
        if isinstance(obj, dict):
            return json.dumps(obj, indent=2)
        else:
            return format(json.loads(obj))
    except ValueError:
        return obj
