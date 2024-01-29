from time import time, time_ns

from mmisp.db.models.user import User


def generate_user() -> User:
    """These fields need to be set manually: org_id, server_id, role_id"""
    return User(
        password="encrypt me",  # TODO
        email=f"site-admin-user+{time_ns()}@test.com",
        autoalert=False,
        authkey="auth key",
        invited_by=0,
        gpgkey="",
        certif_public="",
        nids_sid=12345,  # TODO I don't know what this is
        termsaccepted=True,
        newsread=0,
        change_pw=False,
        contactalert=False,
        disabled=False,
        expiration=None,
        current_login=time(),
        last_login=time(),
        force_logout=False,
        date_created=time(),
        date_modified=time(),
        sub=None,
        external_auth_required=False,
        external_auth_key="",
        last_api_access=time(),
        notification_daily=False,
        notification_weekly=False,
        notification_monthly=False,
        totp=None,
        hotp_counter=None,
        last_pw_change=time(),
    )
