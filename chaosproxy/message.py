import json
import xml.dom.minidom

JSON = 'json'
XML = 'xml'


def format(obj='', content_type=None):
    """
    Utility method to format strings, if is not a json/xml string it returns the original object
    :param content_type: the content type to pretty print
    :param obj: the object to format
    :return: the formatted string if json/xml, otherwise the same object
    """
    if not content_type or not obj:
        return obj

    if XML in content_type:
        return xml.dom.minidom.parseString(obj).toprettyxml(indent='  ')
    elif JSON in content_type:
        return json.dumps(obj, indent=2)
    else:
        return obj
