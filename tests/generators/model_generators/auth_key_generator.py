import time

from mmisp.db.models.auth_key import AuthKey
from mmisp.util.crypto import hash_secret


def generate_auth_key() -> AuthKey:
    """These fields need to be set manually: user_id, [authkey, authkey_start, authkey_end]"""
    return AuthKey(
        authkey=hash_secret("test"),
        authkey_start="test",
        authkey_end="test",
        created=int(time.time()),
        comment="test comment",
    )
