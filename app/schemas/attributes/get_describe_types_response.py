from pydantic import BaseModel


class SaneDefaultsAttributesDetailsResponse(BaseModel):
    default_category: str
    to_ids: int


class SaneDefaultsAttributesResponse(BaseModel):
    md5: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha1: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha256: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    filename: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    pdb: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    filename_md5: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    filename_sha1: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    filename_sha256: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    ip_src: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    ip_dst: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    hostname: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    domain: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    domain_ip: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_src: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    eppn: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_dst: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_subject: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_attachment: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    email_body: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    float: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    git_commit_id: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    url: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    http_method: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    user_agent: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    ja3_fingerprint_md5: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    jarm_fingerprint: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    favicon_mmh3: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    hassh_md5: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    hasshserver_md5: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    regkey: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    regkey_value: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    AS: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    snort: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    bro: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    zeek: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    community_id: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    pattern_in_file: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    pattern_in_traffic: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    pattern_in_memory: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_pattern: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    pgp_public_key: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    pgp_private_key: SaneDefaultsAttributesDetailsResponse
    ssh_fingerprint: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    yara: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    stix2_pattern: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sigma: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    gene: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    kusto_query: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    mime_type: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    identity_card_number: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    cookie: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    vulnerability: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    cpe: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    weakness: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    attachment: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    malware_sample: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    link: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    comment: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    text: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    hex: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    other: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    named_pipe: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    mutex: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    process_state: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    target_user: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    target_email: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    target_machine: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    target_org: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    target_location: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    target_external: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    btc: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    dash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    xmr: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    iban: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    bic: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    bank_account_nr: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    aba_rtn: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    bin: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    cc_number: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    prtn: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    phone_number: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    threat_actor: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    campaign_name: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    campaign_id: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    malware_type: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    uri: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    authentihash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    vhash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    ssdeep: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    imphash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    telfhash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    pehash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    impfuzzy: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha224: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha384: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha512: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha512_224: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha512_256: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha3_224: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha3_256: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha3_384: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    sha3_512: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    tlsh: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    cdhash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    filename_authentihash: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_vhash: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    filename_ssdeep: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_imphash: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_impfuzzy: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_pehash: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha224: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha384: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha512: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha512_224: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha512_256: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha3_224: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha3_256: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha3_384: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_sha3_512: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    filename_tlsh: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    windows_scheduled_task: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    windows_service_name: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    windows_service_displayname: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    whois_registrant_email: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    whois_registrant_phone: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    whois_registrant_name: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    whois_registrant_org: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    whois_registrar: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    whois_creation_date: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    x509_fingerprint_sha1: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    x509_fingerprint_md5: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    x509_fingerprint_sha256: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    dns_soa_email: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    size_in_bytes: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    counter: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    datetime: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    port: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    ip_dst_port: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    ip_src_port: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    hostname_port: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    mac_address: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    mac_eui_64: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_dst_display_name: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    email_src_display_name: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    email_header: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_reply_to: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_x_mailer: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    email_mime_boundary: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    email_thread_index: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    email_message_id: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    github_username: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    github_repository: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    github_organisation: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    jabber_id: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    twitter_id: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    dkim: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    dkim_signature: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    first_name: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    middle_name: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    last_name: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    full_name: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    date_of_birth: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    place_of_birth: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    gender: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    passport_number: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    passport_country: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    passport_expiration: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    redress_number: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    nationality: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    visa_number: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    issue_date_of_the_visa: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    primary_residence: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    country_of_residence: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    special_service_request: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    frequent_flyer_number: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    travel_details: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    payment_details: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    place_port_of_original_embarkation: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    place_port_of_clearance: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    place_port_of_onward_foreign_destination: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    passenger_name_record_locator_number: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    mobile_application_id: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    azure_application_id: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    chrome_extension_id: SaneDefaultsAttributesDetailsResponse(
        default_category="", to_ids=1
    )
    cortex: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    boolean: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)
    anonymised: SaneDefaultsAttributesDetailsResponse(default_category="", to_ids=1)


class SaneDefaultsResponse(BaseModel):
    sane_defaults: str


class TypesResponse(BaseModel):
    types: list[str] = [
        "md5",
        "sha1",
        "sha256",
        "filename",
        "pdb",
        "filename|md5",
        "filename|sha1",
        "filename|sha256",
        "ip-src",
        "ip-dst",
        "hostname",
        "domain",
        "domain|ip",
        "email",
        "email-src",
        "eppn",
        "email-dst",
        "email-subject",
        "email-attachment",
        "email-body",
        "float",
        "git-commit-id",
        "url",
        "http-method",
        "user-agent",
        "ja3-fingerprint-md5",
        "jarm-fingerprint",
        "favicon-mmh3",
        "hassh-md5",
        "hasshserver-md5",
        "regkey",
        "regkey|value",
        "AS",
        "snort",
        "bro",
        "zeek",
        "community-id",
        "pattern-in-file",
        "pattern-in-traffic",
        "pattern-in-memory",
        "filename-pattern",
        "pgp-public-key",
        "pgp-private-key",
        "ssh-fingerprint",
        "yara",
        "stix2-pattern",
        "sigma",
        "gene",
        "kusto-query",
        "mime-type",
        "identity-card-number",
        "cookie",
        "vulnerability",
        "cpe",
        "weakness",
        "attachment",
        "malware-sample",
        "link",
        "comment",
        "text",
        "hex",
        "other",
        "named pipe",
        "mutex",
        "process-state",
        "target-user",
        "target-email",
        "target-machine",
        "target-org",
        "target-location",
        "target-external",
        "btc",
        "dash",
        "xmr",
        "iban",
        "bic",
        "bank-account-nr",
        "aba-rtn",
        "bin",
        "cc-number",
        "prtn",
        "phone-number",
        "threat-actor",
        "campaign-name",
        "campaign-id",
        "malware-type",
        "uri",
        "authentihash",
        "vhash",
        "ssdeep",
        "imphash",
        "telfhash",
        "pehash",
        "impfuzzy",
        "sha224",
        "sha384",
        "sha512",
        "sha512/224",
        "sha512/256",
        "sha3-224",
        "sha3-256",
        "sha3-384",
        "sha3-512",
        "tlsh",
        "cdhash",
        "filename|authentihash",
        "filename|vhash",
        "filename|ssdeep",
        "filename|imphash",
        "filename|impfuzzy",
        "filename|pehash",
        "filename|sha224",
        "filename|sha384",
        "filename|sha512",
        "filename|sha512/224",
        "filename|sha512/256",
        "filename|sha3-224",
        "filename|sha3-256",
        "filename|sha3-384",
        "filename|sha3-512",
        "filename|tlsh",
        "windows-scheduled-task",
        "windows-service-name",
        "windows-service-displayname",
        "whois-registrant-email",
        "whois-registrant-phone",
        "whois-registrant-name",
        "whois-registrant-org",
        "whois-registrar",
        "whois-creation-date",
        "x509-fingerprint-sha1",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha256",
        "dns-soa-email",
        "size-in-bytes",
        "counter",
        "datetime",
        "port",
        "ip-dst|port",
        "ip-src|port",
        "hostname|port",
        "mac-address",
        "mac-eui-64",
        "email-dst-display-name",
        "email-src-display-name",
        "email-header",
        "email-reply-to",
        "email-x-mailer",
        "email-mime-boundary",
        "email-thread-index",
        "email-message-id",
        "github-username",
        "github-repository",
        "github-organisation",
        "jabber-id",
        "twitter-id",
        "dkim",
        "dkim-signature",
        "first-name",
        "middle-name",
        "last-name",
        "full-name",
        "date-of-birth",
        "place-of-birth",
        "gender",
        "passport-number",
        "passport-country",
        "passport-expiration",
        "redress-number",
        "nationality",
        "visa-number",
        "issue-date-of-the-visa",
        "primary-residence",
        "country-of-residence",
        "special-service-request",
        "frequent-flyer-number",
        "travel-details",
        "payment-details",
        "place-port-of-original-embarkation",
        "place-port-of-clearance",
        "place-port-of-onward-foreign-destination",
        "passenger-name-record-locator-number",
        "mobile-application-id",
        "azure-application-id",
        "chrome-extension-id",
        "cortex",
        "boolean",
        "anonymised",
    ]


class CategoriesResponse(BaseModel):
    categories: list[str] = [
        "Internal reference",
        "Targeting data",
        "Antivirus detection",
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Persistence mechanism",
        "Network activity",
        "Payload type",
        "Attribution",
        "External analysis",
        "Financial fraud",
        "Support Tool",
        "Social network",
        "Person",
        "Other",
    ]


class CategoryTypeMappingsResponse(BaseModel):
    Internal_reference: list[str] = [
        "text",
        "link",
        "comment",
        "other",
        "hex",
        "anonymised",
        "git-commit-id",
    ]
    Targeting_data: list[str] = [
        "target-user",
        "target-email",
        "target-machine",
        "target-org",
        "target-location",
        "target-external",
        "comment",
        "anonymised",
    ]
    Antivirus_detection: list[str] = [
        "link",
        "comment",
        "text",
        "hex",
        "attachment",
        "other",
        "anonymised",
    ]
    Payload_delivery: list[str] = [
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "sha512/224",
        "sha512/256",
        "sha3-224",
        "sha3-256",
        "sha3-384",
        "sha3-512",
        "ssdeep",
        "imphash",
        "telfhash",
        "impfuzzy",
        "authentihash",
        "vhash",
        "pehash",
        "tlsh",
        "cdhash",
        "filename",
        "filename|md5",
        "filename|sha1",
        "filename|sha224",
        "filename|sha256",
        "filename|sha384",
        "filename|sha512",
        "filename|sha512/224",
        "filename|sha512/256",
        "filename|sha3-224",
        "filename|sha3-256",
        "filename|sha3-384",
        "filename|sha3-512",
        "filename|authentihash",
        "filename|vhash",
        "filename|ssdeep",
        "filename|tlsh",
        "filename|imphash",
        "filename|impfuzzy",
        "filename|pehash",
        "mac-address",
        "mac-eui-64",
        "ip-src",
        "ip-dst",
        "ip-dst|port",
        "ip-src|port",
        "hostname",
        "domain",
        "email",
        "email-src",
        "email-dst",
        "email-subject",
        "email-attachment",
        "email-body",
        "url",
        "user-agent",
        "AS",
        "pattern-in-file",
        "pattern-in-traffic",
        "filename-pattern",
        "stix2-pattern",
        "yara",
        "sigma",
        "mime-type",
        "attachment",
        "malware-sample",
        "link",
        "malware-type",
        "comment",
        "text",
        "hex",
        "vulnerability",
        "cpe",
        "weakness",
        "x509-fingerprint-sha1",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha256",
        "ja3-fingerprint-md5",
        "jarm-fingerprint",
        "hassh-md5",
        "hasshserver-md5",
        "other",
        "hostname|port",
        "email-dst-display-name",
        "email-src-display-name",
        "email-header",
        "email-reply-to",
        "email-x-mailer",
        "email-mime-boundary",
        "email-thread-index",
        "email-message-id",
        "azure-application-id",
        "mobile-application-id",
        "chrome-extension-id",
        "whois-registrant-email",
        "anonymised",
    ]
    Artifacts_dropped: list[str] = [
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "sha512/224",
        "sha512/256",
        "sha3-224",
        "sha3-256",
        "sha3-384",
        "sha3-512",
        "ssdeep",
        "imphash",
        "telfhash",
        "impfuzzy",
        "authentihash",
        "vhash",
        "cdhash",
        "filename",
        "filename|md5",
        "filename|sha1",
        "filename|sha224",
        "filename|sha256",
        "filename|sha384",
        "filename|sha512",
        "filename|sha512/224",
        "filename|sha512/256",
        "filename|sha3-224",
        "filename|sha3-256",
        "filename|sha3-384",
        "filename|sha3-512",
        "filename|authentihash",
        "filename|vhash",
        "filename|ssdeep",
        "filename|tlsh",
        "filename|imphash",
        "filename|impfuzzy",
        "filename|pehash",
        "regkey",
        "regkey|value",
        "pattern-in-file",
        "pattern-in-memory",
        "filename-pattern",
        "pdb",
        "stix2-pattern",
        "yara",
        "sigma",
        "attachment",
        "malware-sample",
        "named pipe",
        "mutex",
        "process-state",
        "windows-scheduled-task",
        "windows-service-name",
        "windows-service-displayname",
        "comment",
        "text",
        "hex",
        "x509-fingerprint-sha1",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha256",
        "other",
        "cookie",
        "gene",
        "kusto-query",
        "mime-type",
        "anonymised",
        "pgp-public-key",
        "pgp-private-key",
    ]
    Payload_installation: list[str] = [
        "md5",
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "sha512/224",
        "sha512/256",
        "sha3-224",
        "sha3-256",
        "sha3-384",
        "sha3-512",
        "ssdeep",
        "imphash",
        "telfhash",
        "impfuzzy",
        "authentihash",
        "vhash",
        "pehash",
        "tlsh",
        "cdhash",
        "filename",
        "filename|md5",
        "filename|sha1",
        "filename|sha224",
        "filename|sha256",
        "filename|sha384",
        "filename|sha512",
        "filename|sha512/224",
        "filename|sha512/256",
        "filename|sha3-224",
        "filename|sha3-256",
        "filename|sha3-384",
        "filename|sha3-512",
        "filename|authentihash",
        "filename|vhash",
        "filename|ssdeep",
        "filename|tlsh",
        "filename|imphash",
        "filename|impfuzzy",
        "filename|pehash",
        "pattern-in-file",
        "pattern-in-traffic",
        "pattern-in-memory",
        "filename-pattern",
        "stix2-pattern",
        "yara",
        "sigma",
        "vulnerability",
        "cpe",
        "weakness",
        "attachment",
        "malware-sample",
        "malware-type",
        "comment",
        "text",
        "hex",
        "x509-fingerprint-sha1",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha256",
        "azure-application-id",
        "azure-application-id",
        "mobile-application-id",
        "chrome-extension-id",
        "other",
        "mime-type",
        "anonymised",
    ]
    Persistence_mechanism: list[str] = [
        "filename",
        "regkey",
        "regkey|value",
        "comment",
        "text",
        "other",
        "hex",
        "anonymised",
    ]
    Network_activity: list[str] = [
        "ip-src",
        "ip-dst",
        "ip-dst|port",
        "ip-src|port",
        "port",
        "hostname",
        "domain",
        "domain|ip",
        "mac-address",
        "mac-eui-64",
        "email",
        "email-dst",
        "email-src",
        "eppn",
        "url",
        "uri",
        "user-agent",
        "http-method",
        "AS",
        "snort",
        "pattern-in-file",
        "filename-pattern",
        "stix2-pattern",
        "pattern-in-traffic",
        "attachment",
        "comment",
        "text",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha1",
        "x509-fingerprint-sha256",
        "ja3-fingerprint-md5",
        "jarm-fingerprint",
        "hassh-md5",
        "hasshserver-md5",
        "other",
        "hex",
        "cookie",
        "hostname|port",
        "bro",
        "zeek",
        "anonymised",
        "community-id",
        "email-subject",
        "favicon-mmh3",
        "dkim",
        "dkim-signature",
        "ssh-fingerprint",
    ]
    Payload_type: list[str] = ["comment", "text", "other", "anonymised"]
    Attribution: list[str] = [
        "threat-actor",
        "campaign-name",
        "campaign-id",
        "whois-registrant-phone",
        "whois-registrant-email",
        "whois-registrant-name",
        "whois-registrant-org",
        "whois-registrar",
        "whois-creation-date",
        "comment",
        "text",
        "x509-fingerprint-sha1",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha256",
        "other",
        "dns-soa-email",
        "anonymised",
        "email",
    ]
    External_analysis: list[str] = [
        "md5",
        "sha1",
        "sha256",
        "sha3-224",
        "sha3-256",
        "sha3-384",
        "sha3-512",
        "filename",
        "filename|md5",
        "filename|sha1",
        "filename|sha256",
        "filename|sha3-224",
        "filename|sha3-256",
        "filename|sha3-384",
        "filename|sha3-512",
        "ip-src",
        "ip-dst",
        "ip-dst|port",
        "ip-src|port",
        "mac-address",
        "mac-eui-64",
        "hostname",
        "domain",
        "domain|ip",
        "url",
        "user-agent",
        "regkey",
        "regkey|value",
        "AS",
        "snort",
        "bro",
        "zeek",
        "pattern-in-file",
        "pattern-in-traffic",
        "pattern-in-memory",
        "filename-pattern",
        "vulnerability",
        "cpe",
        "weakness",
        "attachment",
        "malware-sample",
        "link",
        "comment",
        "text",
        "x509-fingerprint-sha1",
        "x509-fingerprint-md5",
        "x509-fingerprint-sha256",
        "ja3-fingerprint-md5",
        "jarm-fingerprint",
        "hassh-md5",
        "hasshserver-md5",
        "github-repository",
        "other",
        "cortex",
        "anonymised",
        "community-id",
    ]
    Financial_fraud: list[str] = [
        "btc",
        "dash",
        "xmr",
        "iban",
        "bic",
        "bank-account-nr",
        "aba-rtn",
        "bin",
        "cc-number",
        "prtn",
        "phone-number",
        "comment",
        "text",
        "other",
        "hex",
        "anonymised",
    ]
    Support_Tool: list[str] = [
        "link",
        "text",
        "attachment",
        "comment",
        "other",
        "hex",
        "anonymised",
    ]
    Social_network: list[str] = [
        "github-username",
        "github-repository",
        "github-organisation",
        "jabber-id",
        "twitter-id",
        "email",
        "email-src",
        "email-dst",
        "eppn",
        "comment",
        "text",
        "other",
        "whois-registrant-email",
        "anonymised",
        "pgp-public-key",
        "pgp-private-key",
    ]
    Person: list[str] = [
        "first-name",
        "middle-name",
        "last-name",
        "full-name",
        "date-of-birth",
        "place-of-birth",
        "gender",
        "passport-number",
        "passport-country",
        "passport-expiration",
        "redress-number",
        "nationality",
        "visa-number",
        "issue-date-of-the-visa",
        "primary-residence",
        "country-of-residence",
        "special-service-request",
        "frequent-flyer-number",
        "travel-details",
        "payment-details",
        "place-port-of-original-embarkation",
        "place-port-of-clearance",
        "place-port-of-onward-foreign-destination",
        "passenger-name-record-locator-number",
        "comment",
        "text",
        "other",
        "phone-number",
        "identity-card-number",
        "anonymised",
        "email",
        "pgp-public-key",
        "pgp-private-key",
    ]
    Other: list[str] = [
        "comment",
        "text",
        "other",
        "size-in-bytes",
        "counter",
        "datetime",
        "cpe",
        "port",
        "float",
        "hex",
        "phone-number",
        "boolean",
        "anonymised",
        "pgp-public-key",
        "pgp-private-key",
    ]


class DescribeTypesAttributesResponse(BaseModel):
    sane_defaults: SaneDefaultsResponse
    types: TypesResponse
    categories: CategoriesResponse
    category_type_mappings: CategoryTypeMappingsResponse


class DescribeTypesResponse(BaseModel):
    result: str

    class Config:
        orm_mode = True
