import os
from logging.config import dictConfig

import pem
from jwcrypto.jwk import JWK

# Logging Config
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# App Config
hostname = os.getenv('HOST_URL', 'http://localhost:5000')
token_validity = os.getenv('TOKEN_VALIDITY_SECONDS', 3600)
jwk = JWK.generate(
    kty='RSA',
    size=2048,
    kid='fake-oidc',
    use='sig',
    alg='RS256'
)
