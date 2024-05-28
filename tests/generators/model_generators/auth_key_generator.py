import string

from nanoid import generate

from mmisp.db.models.auth_key import AuthKey
from mmisp.util.crypto import hash_secret


def generate_auth_key() -> AuthKey:
    """These fields need to be set manually: user_id, [authkey, authkey_start, authkey_end]"""
    clear_key = generate(string.ascii_letters + string.digits, size=40)

    return AuthKey(
        authkey=hash_secret(clear_key),
        authkey_start=clear_key[:4],
        authkey_end=clear_key[-4:],
        comment="test comment",
    )
