from pydantic import BaseModel


class SaneDefaultsAttributesDetailsResponse(BaseModel):
    default_category: str
    to_ids: int


class SaneDefaultsAttributesResponse(BaseModel):
    md5: SaneDefaultsAttributesDetailsResponse
    sha1: SaneDefaultsAttributesDetailsResponse
    sha256: SaneDefaultsAttributesDetailsResponse
    filename: SaneDefaultsAttributesDetailsResponse
    pdb: SaneDefaultsAttributesDetailsResponse
    filename_md5: SaneDefaultsAttributesDetailsResponse
    filename_sha1: SaneDefaultsAttributesDetailsResponse
    filename_sha256: SaneDefaultsAttributesDetailsResponse
    ip_src: SaneDefaultsAttributesDetailsResponse
    ip_dst: SaneDefaultsAttributesDetailsResponse
    hostname: SaneDefaultsAttributesDetailsResponse
    domain: SaneDefaultsAttributesDetailsResponse
    domain_ip: SaneDefaultsAttributesDetailsResponse
    email: SaneDefaultsAttributesDetailsResponse
    email_src: SaneDefaultsAttributesDetailsResponse
    eppn: SaneDefaultsAttributesDetailsResponse
    email_dst: SaneDefaultsAttributesDetailsResponse
    email_subject: SaneDefaultsAttributesDetailsResponse
    email_attachment: SaneDefaultsAttributesDetailsResponse
    email_body: SaneDefaultsAttributesDetailsResponse
    float: SaneDefaultsAttributesDetailsResponse
    git_commit_id: SaneDefaultsAttributesDetailsResponse
    url: SaneDefaultsAttributesDetailsResponse
    http_method: SaneDefaultsAttributesDetailsResponse
    user_agent: SaneDefaultsAttributesDetailsResponse
    ja3_fingerprint_md5: SaneDefaultsAttributesDetailsResponse
    jarm_fingerprint: SaneDefaultsAttributesDetailsResponse
    favicon_mmh3: SaneDefaultsAttributesDetailsResponse
    hassh_md5: SaneDefaultsAttributesDetailsResponse
    hasshserver_md5: SaneDefaultsAttributesDetailsResponse
    regkey: SaneDefaultsAttributesDetailsResponse
    regkey_value: SaneDefaultsAttributesDetailsResponse
    AS: SaneDefaultsAttributesDetailsResponse
    snort: SaneDefaultsAttributesDetailsResponse
    bro: SaneDefaultsAttributesDetailsResponse
    zeek: SaneDefaultsAttributesDetailsResponse
    community_id: SaneDefaultsAttributesDetailsResponse
    pattern_in_file: SaneDefaultsAttributesDetailsResponse
    pattern_in_traffic: SaneDefaultsAttributesDetailsResponse
    pattern_in_memory: SaneDefaultsAttributesDetailsResponse
    filename_pattern: SaneDefaultsAttributesDetailsResponse
    pgp_public_key: SaneDefaultsAttributesDetailsResponse
    pgp_private_key: SaneDefaultsAttributesDetailsResponse
    ssh_fingerprint: SaneDefaultsAttributesDetailsResponse
    yara: SaneDefaultsAttributesDetailsResponse
    stix2_pattern: SaneDefaultsAttributesDetailsResponse
    sigma: SaneDefaultsAttributesDetailsResponse
    gene: SaneDefaultsAttributesDetailsResponse
    kusto_query: SaneDefaultsAttributesDetailsResponse
    mime_type: SaneDefaultsAttributesDetailsResponse
    identity_card_number: SaneDefaultsAttributesDetailsResponse
    cookie: SaneDefaultsAttributesDetailsResponse
    vulnerability: SaneDefaultsAttributesDetailsResponse
    cpe: SaneDefaultsAttributesDetailsResponse
    weakness: SaneDefaultsAttributesDetailsResponse
    attachment: SaneDefaultsAttributesDetailsResponse
    malware_sample: SaneDefaultsAttributesDetailsResponse
    link: SaneDefaultsAttributesDetailsResponse
    comment: SaneDefaultsAttributesDetailsResponse
    text: SaneDefaultsAttributesDetailsResponse
    hex: SaneDefaultsAttributesDetailsResponse
    other: SaneDefaultsAttributesDetailsResponse
    named_pipe: SaneDefaultsAttributesDetailsResponse
    mutex: SaneDefaultsAttributesDetailsResponse
    process_state: SaneDefaultsAttributesDetailsResponse
    target_user: SaneDefaultsAttributesDetailsResponse
    target_email: SaneDefaultsAttributesDetailsResponse
    target_machine: SaneDefaultsAttributesDetailsResponse
    target_org: SaneDefaultsAttributesDetailsResponse
    target_location: SaneDefaultsAttributesDetailsResponse
    target_external: SaneDefaultsAttributesDetailsResponse
    btc: SaneDefaultsAttributesDetailsResponse
    dash: SaneDefaultsAttributesDetailsResponse
    xmr: SaneDefaultsAttributesDetailsResponse
    iban: SaneDefaultsAttributesDetailsResponse
    bic: SaneDefaultsAttributesDetailsResponse
    bank_account_nr: SaneDefaultsAttributesDetailsResponse
    aba_rtn: SaneDefaultsAttributesDetailsResponse
    bin: SaneDefaultsAttributesDetailsResponse
    cc_number: SaneDefaultsAttributesDetailsResponse
    prtn: SaneDefaultsAttributesDetailsResponse
    phone_number: SaneDefaultsAttributesDetailsResponse
    threat_actor: SaneDefaultsAttributesDetailsResponse
    campaign_name: SaneDefaultsAttributesDetailsResponse
    campaign_id: SaneDefaultsAttributesDetailsResponse
    malware_type: SaneDefaultsAttributesDetailsResponse
    uri: SaneDefaultsAttributesDetailsResponse
    authentihash: SaneDefaultsAttributesDetailsResponse
    vhash: SaneDefaultsAttributesDetailsResponse
    ssdeep: SaneDefaultsAttributesDetailsResponse
    imphash: SaneDefaultsAttributesDetailsResponse
    telfhash: SaneDefaultsAttributesDetailsResponse
    pehash: SaneDefaultsAttributesDetailsResponse
    impfuzzy: SaneDefaultsAttributesDetailsResponse
    sha224: SaneDefaultsAttributesDetailsResponse
    sha384: SaneDefaultsAttributesDetailsResponse
    sha512: SaneDefaultsAttributesDetailsResponse
    sha512_224: SaneDefaultsAttributesDetailsResponse
    sha512_256: SaneDefaultsAttributesDetailsResponse
    sha3_224: SaneDefaultsAttributesDetailsResponse
    sha3_256: SaneDefaultsAttributesDetailsResponse
    sha3_384: SaneDefaultsAttributesDetailsResponse
    sha3_512: SaneDefaultsAttributesDetailsResponse
    tlsh: SaneDefaultsAttributesDetailsResponse
    cdhash: SaneDefaultsAttributesDetailsResponse
    filename_authentihash: SaneDefaultsAttributesDetailsResponse
    filename_vhash: SaneDefaultsAttributesDetailsResponse
    filename_ssdeep: SaneDefaultsAttributesDetailsResponse
    filename_imphash: SaneDefaultsAttributesDetailsResponse
    filename_impfuzzy: SaneDefaultsAttributesDetailsResponse
    filename_pehash: SaneDefaultsAttributesDetailsResponse
    filename_sha224: SaneDefaultsAttributesDetailsResponse
    filename_sha384: SaneDefaultsAttributesDetailsResponse
    filename_sha512: SaneDefaultsAttributesDetailsResponse
    filename_sha512_224: SaneDefaultsAttributesDetailsResponse
    filename_sha512_256: SaneDefaultsAttributesDetailsResponse
    filename_sha3_224: SaneDefaultsAttributesDetailsResponse
    filename_sha3_256: SaneDefaultsAttributesDetailsResponse
    filename_sha3_384: SaneDefaultsAttributesDetailsResponse
    filename_sha3_512: SaneDefaultsAttributesDetailsResponse
    filename_tlsh: SaneDefaultsAttributesDetailsResponse
    windows_scheduled_task: SaneDefaultsAttributesDetailsResponse
    windows_service_name: SaneDefaultsAttributesDetailsResponse
    windows_service_displayname: SaneDefaultsAttributesDetailsResponse
    whois_registrant_email: SaneDefaultsAttributesDetailsResponse
    whois_registrant_phone: SaneDefaultsAttributesDetailsResponse
    whois_registrant_name: SaneDefaultsAttributesDetailsResponse
    whois_registrant_org: SaneDefaultsAttributesDetailsResponse
    whois_registrar: SaneDefaultsAttributesDetailsResponse
    whois_creation_date: SaneDefaultsAttributesDetailsResponse
    x509_fingerprint_sha1: SaneDefaultsAttributesDetailsResponse
    x509_fingerprint_md5: SaneDefaultsAttributesDetailsResponse
    x509_fingerprint_sha256: SaneDefaultsAttributesDetailsResponse
    dns_soa_email: SaneDefaultsAttributesDetailsResponse
    size_in_bytes: SaneDefaultsAttributesDetailsResponse
    counter: SaneDefaultsAttributesDetailsResponse
    datetime: SaneDefaultsAttributesDetailsResponse
    port: SaneDefaultsAttributesDetailsResponse
    ip_dst_port: SaneDefaultsAttributesDetailsResponse
    ip_src_port: SaneDefaultsAttributesDetailsResponse
    hostname_port: SaneDefaultsAttributesDetailsResponse
    mac_address: SaneDefaultsAttributesDetailsResponse
    mac_eui_64: SaneDefaultsAttributesDetailsResponse
    email_dst_display_name: SaneDefaultsAttributesDetailsResponse
    email_src_display_name: SaneDefaultsAttributesDetailsResponse
    email_header: SaneDefaultsAttributesDetailsResponse
    email_reply_to: SaneDefaultsAttributesDetailsResponse
    email_x_mailer: SaneDefaultsAttributesDetailsResponse
    email_mime_boundary: SaneDefaultsAttributesDetailsResponse
    email_thread_index: SaneDefaultsAttributesDetailsResponse
    email_message_id: SaneDefaultsAttributesDetailsResponse
    github_username: SaneDefaultsAttributesDetailsResponse
    github_repository: SaneDefaultsAttributesDetailsResponse
    github_organisation: SaneDefaultsAttributesDetailsResponse
    jabber_id: SaneDefaultsAttributesDetailsResponse
    twitter_id: SaneDefaultsAttributesDetailsResponse
    dkim: SaneDefaultsAttributesDetailsResponse
    dkim_signature: SaneDefaultsAttributesDetailsResponse
    first_name: SaneDefaultsAttributesDetailsResponse
    middle_name: SaneDefaultsAttributesDetailsResponse
    last_name: SaneDefaultsAttributesDetailsResponse
    full_name: SaneDefaultsAttributesDetailsResponse
    date_of_birth: SaneDefaultsAttributesDetailsResponse
    place_of_birth: SaneDefaultsAttributesDetailsResponse
    gender: SaneDefaultsAttributesDetailsResponse
    passport_number: SaneDefaultsAttributesDetailsResponse
    passport_country: SaneDefaultsAttributesDetailsResponse
    passport_expiration: SaneDefaultsAttributesDetailsResponse
    redress_number: SaneDefaultsAttributesDetailsResponse
    nationality: SaneDefaultsAttributesDetailsResponse
    visa_number: SaneDefaultsAttributesDetailsResponse
    issue_date_of_the_visa: SaneDefaultsAttributesDetailsResponse
    primary_residence: SaneDefaultsAttributesDetailsResponse
    country_of_residence: SaneDefaultsAttributesDetailsResponse
    special_service_request: SaneDefaultsAttributesDetailsResponse
    frequent_flyer_number: SaneDefaultsAttributesDetailsResponse
    travel_details: SaneDefaultsAttributesDetailsResponse
    payment_details: SaneDefaultsAttributesDetailsResponse
    place_port_of_original_embarkation: SaneDefaultsAttributesDetailsResponse
    place_port_of_clearance: SaneDefaultsAttributesDetailsResponse
    place_port_of_onward_foreign_destination: SaneDefaultsAttributesDetailsResponse
    passenger_name_record_locator_number: SaneDefaultsAttributesDetailsResponse
    mobile_application_id: SaneDefaultsAttributesDetailsResponse
    azure_application_id: SaneDefaultsAttributesDetailsResponse
    chrome_extension_id: SaneDefaultsAttributesDetailsResponse
    cortex: SaneDefaultsAttributesDetailsResponse
    boolean: SaneDefaultsAttributesDetailsResponse
    anonymised: SaneDefaultsAttributesDetailsResponse


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
