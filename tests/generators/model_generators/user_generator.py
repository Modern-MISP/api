from time import time, time_ns

from mmisp.db.models.user import User
from mmisp.util.crypto import hash_secret


def generate_user() -> User:
    """These fields need to be set manually: org_id, role_id"""
    return User(
        password=hash_secret("test"),
        email=f"generated-user+{time_ns()}@test.com",
        autoalert=False,
        authkey="auth key",
        invited_by=0,
        gpgkey="",
        certif_public="",
        nids_sid=12345,  # unused
        termsaccepted=True,
        newsread=0,
        change_pw=False,
        contactalert=False,
        disabled=False,
        expiration=None,
        current_login=time(),
        last_login=time(),
        force_logout=False,
    )
