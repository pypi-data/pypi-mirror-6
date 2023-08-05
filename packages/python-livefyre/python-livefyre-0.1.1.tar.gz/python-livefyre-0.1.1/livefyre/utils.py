from datetime import datetime, timedelta
import re
import time

import jwt


def create_auth_token(user_id,
                      network,
                      network_secret,
                      display_name=None,
                      expires=None):
    """ """

    expires = expires or datetime.now() + timedelta(hours=24)
    token = {
        'domain': '{}.fyre.co'.format(network),
        'user_id': user_id,
        'expires': time.mktime(expires.timetuple()),
        'display_name': display_name or user_id,
    }
    print token

    return jwt_encode(token, network_secret)


def jid(user_id, network):
    return "{}@{}.fyre.co".format(user_id, network)


def jwt_encode(payload, secret):
    """Uses SHA-256 per Livefyre doc specs"""
    return jwt.encode(payload, secret, "HS256")


def _validate_url(url):
    url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(re.match(url_regex, url))

# Django includes a really nice URL validator, try using it if it's installed
# otherwise use the above simple validator
try:
    from django.core.validators import URLValidator
    validate_url = URLValidator(verify_exists=False)
except ImportError:
    validate_url = _validate_url
