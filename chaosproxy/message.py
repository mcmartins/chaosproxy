import json


def format(obj):
    if not obj:
        obj = ''
    try:
        if isinstance(obj, dict):
            return json.dumps(obj, indent=2)
        else:
            return format(json.loads(obj))
    except ValueError:
        return obj
