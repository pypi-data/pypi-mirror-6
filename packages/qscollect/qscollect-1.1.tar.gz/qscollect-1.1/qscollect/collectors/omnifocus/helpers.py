import datetime
import pytz

NAMESPACE = "{http://www.omnigroup.com/namespace/OmniFocus/v1}"


def _NS(tag):
    if tag.startswith(NAMESPACE):
        return tag

    return "".join((NAMESPACE, tag))


def _NS_STRIP(tag):
    if tag.startswith(NAMESPACE):
        return tag[len(NAMESPACE):]

    return tag


def normalize_date(value, tzinfo=pytz.utc):
    """ Dates need to be tz aware """
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=tzinfo)
    return value