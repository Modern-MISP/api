from mmisp.db.models.auth_key import AuthKey
from mmisp.util.crypto import hash_auth_key


def generate_auth_key() -> AuthKey:
    """These fields need to be set manually: user_id, [authkey]"""
    return AuthKey(
        authkey=hash_auth_key("test"),
        authkey_start="test",
        authkey_end="test",
        comment="test comment",
    )
