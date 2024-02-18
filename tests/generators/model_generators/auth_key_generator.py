from mmisp.db.models.auth_key import AuthKey
from mmisp.util.crypto import hash_password


def generate_auth_key() -> AuthKey:
    """These fields need to be set manually: user_id"""
    return AuthKey(
        authkey=hash_password("test"),
        authkey_start="test",
        authkey_end="test",
        comment="test comment",
    )
