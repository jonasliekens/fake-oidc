from datetime import datetime, timedelta

import config


# https://www.rfc-editor.org/rfc/rfc7662
def create_introspect_response(principal):
    now = datetime.now()

    return {
        'active': True,
        'username': principal['preferred_username'],
        'exp': round((now + timedelta(seconds=config.token_validity)).timestamp()),
        'iat': round(now.timestamp()),
        'iss': config.hostname
    }
