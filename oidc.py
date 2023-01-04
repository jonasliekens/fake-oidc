import json
from datetime import datetime, timedelta

from jwcrypto import jwt

import config
import users
from utils import calculate_at_hash

oidc_profile_claims = [
    "name",
    "family_name",
    "given_name",
    "middle_name",
    "nickname",
    "preferred_username",
    "profile",
    "picture",
    "website",
    "gender",
    "birthdate",
    "zoneinfo",
    "locale",
    "updated_at"
]
oidc_address_claims = ["address"]
oidc_phone_claims = ["phone_number", "phone_number_verified"]
oidc_email_claims = ["email", "email_verified"]


def generate_id_token(token_data):
    user_token_data = users.find_user_by_token(token_data['access_token'])
    now = datetime.now()
    jwt_claims = {
        'iss': config.hostname,
        'sub': '{0}'.format(users.find_user_by_token(token_data['access_token'])['sub']),
        'aud': token_data['client_id'],
        'exp': round((now + timedelta(seconds=config.token_validity)).timestamp()),
        'iat': round(now.timestamp()),
        'nonce': token_data['nonce'],
        'at_hash': calculate_at_hash(token_data['access_token']),
        'scope': token_data['scope'].replace(',', ' ')
    }

    if str(token_data['scope']).__contains__('profile'):
        append_openid_claims(jwt_claims, oidc_profile_claims, user_token_data)
    if str(token_data['scope']).__contains__('address'):
        append_openid_claims(jwt_claims, oidc_address_claims, user_token_data)
    if str(token_data['scope']).__contains__('phone'):
        append_openid_claims(jwt_claims, oidc_phone_claims, user_token_data)
    if str(token_data['scope']).__contains__('email'):
        append_openid_claims(jwt_claims, oidc_email_claims, user_token_data)

    id_token = jwt.JWT(
        claims=jwt_claims,
        header={
            'kid': json.loads(config.jwk.export_public())['kid'],
            'alg': 'RS256'
        }
    )

    id_token.make_signed_token(key=config.jwk)
    return id_token


def append_openid_claims(jwt_claims, claim_names, user_token_data):
    for claim_name in claim_names:
        if claim_name in user_token_data:
            jwt_claims[claim_name] = user_token_data[claim_name]
