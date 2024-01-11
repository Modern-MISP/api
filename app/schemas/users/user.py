from pydantic import BaseModel


class User(BaseModel):
    id: str
    password: str
    org_id: str
    email: str
    autoalert: bool
    invited_by: str
    gpgkey: str
    certif_public: str
    passwnids_sidord: str
    termsaccepted: bool
    role_id: str
    change_pw: bool
    contactalert: bool
    disabled: bool
    current_login: str  # time in seconds
    last_login: str  # time in seconds
    force_logout: bool
    date_created: str  # time in seconds
    date_modified: str  # time in seconds
    external_auth_required: bool
    external_auth_key: str
    last_api_access: str  # time in seconds
    notification_daily: bool
    notification_weekly: bool
    notification_monthly: bool
    totp: str
    hotp_counter: str
    last_pw_change: str  # time in seconds
