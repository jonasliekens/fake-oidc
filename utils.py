import base64
import hashlib
import random
import string


def random_string(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def calculate_at_hash(token):
    hash_digest = hashlib.sha256(token.encode('utf-8')).digest()
    cut_at = int(len(hash_digest) / 2)
    truncated = hash_digest[:cut_at]
    at_hash = base64url_encode(truncated)
    return at_hash.decode('utf-8')


def base64url_encode(value):
    return base64.urlsafe_b64encode(value).replace(b'=', b'')
