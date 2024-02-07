from pydantic import BaseModel, Field


class GetAttributeStatisticsTypesResponse(BaseModel):
    as_: str = Field(alias="AS")
    attachment: str
    authentihash: str
    boolean: str
    btc: str
    campaign_id: str = Field(alias="campaign-id")
    campaign_name: str = Field(alias="campaign-name")
    comment: str
    cookie: str
    counter: str
    cpe: str
    date_of_birth: str = Field(alias="date-of-birth")
    datetime: str
    dns_soa_email: str = Field(alias="dns-soa-email")
    domain: str
    domain_ip: str = Field(alias="domain|ip")
    email: str
    email_attachment: str = Field(alias="email-attachment")
    email_body: str = Field(alias="email-body")
    email_dst: str = Field(alias="email-dst")
    email_message_id: str = Field(alias="email-message-id")
    email_mime_boundary: str = Field(alias="email-mime-boundary")
    email_reply_to: str = Field(alias="email-reply-to")
    email_src: str = Field(alias="email-src")
    email_src_display_name: str = Field(alias="email-src-display-name")
    email_subject: str = Field(alias="email-subject")
    email_x_mailer: str = Field(alias="email-x-mailer")
    filename: str
    filename_pattern: str = Field(alias="filename-pattern")
    filename_md5: str = Field(alias="filename|md5")
    filename_sha1: str = Field(alias="filename|sha1")
    filename_sha256: str = Field(alias="filename|sha256")
    first_name: str = Field(alias="first-name")
    float: str
    full_name: str = Field(alias="full-name")
    gender: str
    github_repository: str = Field(alias="github-repository")
    github_username: str = Field(alias="github-username")
    hex: str
    hostname: str
    http_method: str = Field(alias="http-method")
    imphash: str
    ip_dst: str = Field(alias="ip-dst")
    ip_dst_port: str = Field(alias="ip-dst|port")
    ip_src: str = Field(alias="ip-src")
    ip_src_port: str = Field(alias="ip-src|port")
    ja3_fingerprint_md5: str = Field(alias="ja3-fingerprint-md5")
    jabber_id: str = Field(alias="jabber-id")
    jarm_fingerprint: str = Field(alias="jarm-fingerprint")
    last_name: str = Field(alias="last-name")
    link: str
    malware_sample: str = Field(alias="malware-sample")
    md5: str
    mime_type: str = Field(alias="mime-type")
    mobile_application_id: str = Field(alias="mobile-application-id")
    mutex: str
    named_pipe: str = Field(alias="named pipe")
    nationality: str
    other: str
    passport_country: str = Field(alias="passport-country")
    passport_expiration: str = Field(alias="passport-expiration")
    passport_number: str = Field(alias="passport-number")
    pattern_in_file: str = Field(alias="pattern-in-file")
    pattern_in_memory: str = Field(alias="pattern-in-memory")
    pattern_in_traffic: str = Field(alias="pattern-in-traffic")
    pdb: str
    pehash: str
    phone_number: str = Field(alias="phone-number")
    place_of_birth: str = Field(alias="place-of-birth")
    port: str
    regkey: str
    regkey_value: str = Field(alias="regkey|value")
    sha1: str
    sha224: str
    sha256: str
    sha384: str
    sha512: str
    sigma: str
    size_in_bytes: str = Field(alias="size-in-bytes")
    snort: str
    ssdeep: str
    stix2_pattern: str = Field(alias="stix2-pattern")
    target_external: str = Field(alias="target-external")
    target_location: str = Field(alias="target-location")
    target_machine: str = Field(alias="target-machine")
    target_org: str = Field(alias="target-org")
    target_user: str = Field(alias="target-user")
    text: str
    threat_actor: str = Field(alias="threat-actor")
    tlsh: str
    uri: str
    url: str
    user_agent: str = Field(alias="user-agent")
    vhash: str
    vulnerability: str
    weakness: str
    whois_creation_date: str = Field(alias="whois-creation-date")
    whois_registrant_email: str = Field(alias="whois-registrant-email")
    whois_registrant_name: str = Field(alias="whois-registrant-name")
    whois_registrant_org: str = Field(alias="whois-registrant-org")
    whois_registrant_phone: str = Field(alias="whois-registrant-phone")
    whois_registrar: str = Field(alias="whois-registrar")
    windows_scheduled_task: str = Field(alias="windows-scheduled-task")
    windows_service_name: str = Field(alias="windows-service-name")
    x509_fingerprint_md5: str = Field(alias="x509-fingerprint-md5")
    x509_fingerprint_sha1: str = Field(alias="x509-fingerprint-sha1")
    x509_fingerprint_sha256: str = Field(alias="x509-fingerprint-sha256")
    yara: str

    class Config:
        orm_mode = True


class GetAttributeStatisticsCategoriesResponse(BaseModel):
    antivirus_detection: str = Field(alias="Antivirus detection")
    artifacts_dropped: str = Field(alias="Artifacts dropped")
    attribution: str = Field(alias="Attribution")
    external_analysis: str = Field(alias="External analysis")
    financial_fraud: str = Field(alias="Financial fraud")
    internal_reference: str = Field(alias="Internal reference")
    network_activity: str = Field(alias="Network activity")
    other: str = Field(alias="Other")
    payload_delivery: str = Field(alias="Payload delivery")
    payload_installation: str = Field(alias="Payload installation")
    payload_type: str = Field(alias="Payload type")
    persistence_mechanism: str = Field(alias="Persistence mechanism")
    person: str = Field(alias="Person")
    social_network: str = Field(alias="Social network")
    support__tool: str = Field(alias="Support Tool")
    targeting_data: str = Field(alias="Targeting data")

    class Config:
        orm_mode = True
