import hashlib
import hmac
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time


def md5(data):
    """
    Calculates the MD5 of the given data or an empty string if the data is not set
    """
    if data:
        if isinstance(data, file):
            data = data.read()
        return hashlib.md5(data).hexdigest()
    else:
        return ''


def rfc1123_date(date=None):
    """
    Formats a date object as required for the HTTP Date field.

    See: http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html
    """
    date = date or datetime.now()
    timestamp = mktime(date.timetuple())
    return format_date_time(timestamp)


def hmac_sha1(key, to_sign):
    """
    Quick & simple HMAC_S
    """
    return hmac.new(key, to_sign, digestmod=hashlib.sha1).digest()
