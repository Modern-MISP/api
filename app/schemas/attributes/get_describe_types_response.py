from pydantic import BaseModel


class GetDescribeTypesSaneDefaultsAttributesDetails(BaseModel):
    default_category: str
    to_ids: int


class GetDescribeTypesSaneDefaultsAttributes(BaseModel):
    md5: GetDescribeTypesSaneDefaultsAttributesDetails
    sha1: GetDescribeTypesSaneDefaultsAttributesDetails
    sha256: GetDescribeTypesSaneDefaultsAttributesDetails
    filename: GetDescribeTypesSaneDefaultsAttributesDetails
    pdb: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_md5: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha1: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha256: GetDescribeTypesSaneDefaultsAttributesDetails
    ip_src: GetDescribeTypesSaneDefaultsAttributesDetails
    ip_dst: GetDescribeTypesSaneDefaultsAttributesDetails
    hostname: GetDescribeTypesSaneDefaultsAttributesDetails
    domain: GetDescribeTypesSaneDefaultsAttributesDetails
    domain_ip: GetDescribeTypesSaneDefaultsAttributesDetails
    email: GetDescribeTypesSaneDefaultsAttributesDetails
    email_src: GetDescribeTypesSaneDefaultsAttributesDetails
    eppn: GetDescribeTypesSaneDefaultsAttributesDetails
    email_dst: GetDescribeTypesSaneDefaultsAttributesDetails
    email_subject: GetDescribeTypesSaneDefaultsAttributesDetails
    email_attachment: GetDescribeTypesSaneDefaultsAttributesDetails
    email_body: GetDescribeTypesSaneDefaultsAttributesDetails
    float: GetDescribeTypesSaneDefaultsAttributesDetails
    git_commit_id: GetDescribeTypesSaneDefaultsAttributesDetails
    url: GetDescribeTypesSaneDefaultsAttributesDetails
    http_method: GetDescribeTypesSaneDefaultsAttributesDetails
    user_agent: GetDescribeTypesSaneDefaultsAttributesDetails
    ja3_fingerprint_md5: GetDescribeTypesSaneDefaultsAttributesDetails
    jarm_fingerprint: GetDescribeTypesSaneDefaultsAttributesDetails
    favicon_mmh3: GetDescribeTypesSaneDefaultsAttributesDetails
    hassh_md5: GetDescribeTypesSaneDefaultsAttributesDetails
    hasshserver_md5: GetDescribeTypesSaneDefaultsAttributesDetails
    regkey: GetDescribeTypesSaneDefaultsAttributesDetails
    regkey_value: GetDescribeTypesSaneDefaultsAttributesDetails
    AS: GetDescribeTypesSaneDefaultsAttributesDetails
    snort: GetDescribeTypesSaneDefaultsAttributesDetails
    bro: GetDescribeTypesSaneDefaultsAttributesDetails
    zeek: GetDescribeTypesSaneDefaultsAttributesDetails
    community_id: GetDescribeTypesSaneDefaultsAttributesDetails
    pattern_in_file: GetDescribeTypesSaneDefaultsAttributesDetails
    pattern_in_traffic: GetDescribeTypesSaneDefaultsAttributesDetails
    pattern_in_memory: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_pattern: GetDescribeTypesSaneDefaultsAttributesDetails
    pgp_public_key: GetDescribeTypesSaneDefaultsAttributesDetails
    pgp_private_key: GetDescribeTypesSaneDefaultsAttributesDetails
    ssh_fingerprint: GetDescribeTypesSaneDefaultsAttributesDetails
    yara: GetDescribeTypesSaneDefaultsAttributesDetails
    stix2_pattern: GetDescribeTypesSaneDefaultsAttributesDetails
    sigma: GetDescribeTypesSaneDefaultsAttributesDetails
    gene: GetDescribeTypesSaneDefaultsAttributesDetails
    kusto_query: GetDescribeTypesSaneDefaultsAttributesDetails
    mime_type: GetDescribeTypesSaneDefaultsAttributesDetails
    identity_card_number: GetDescribeTypesSaneDefaultsAttributesDetails
    cookie: GetDescribeTypesSaneDefaultsAttributesDetails
    vulnerability: GetDescribeTypesSaneDefaultsAttributesDetails
    cpe: GetDescribeTypesSaneDefaultsAttributesDetails
    weakness: GetDescribeTypesSaneDefaultsAttributesDetails
    attachment: GetDescribeTypesSaneDefaultsAttributesDetails
    malware_sample: GetDescribeTypesSaneDefaultsAttributesDetails
    link: GetDescribeTypesSaneDefaultsAttributesDetails
    comment: GetDescribeTypesSaneDefaultsAttributesDetails
    text: GetDescribeTypesSaneDefaultsAttributesDetails
    hex: GetDescribeTypesSaneDefaultsAttributesDetails
    other: GetDescribeTypesSaneDefaultsAttributesDetails
    named_pipe: GetDescribeTypesSaneDefaultsAttributesDetails
    mutex: GetDescribeTypesSaneDefaultsAttributesDetails
    process_state: GetDescribeTypesSaneDefaultsAttributesDetails
    target_user: GetDescribeTypesSaneDefaultsAttributesDetails
    target_email: GetDescribeTypesSaneDefaultsAttributesDetails
    target_machine: GetDescribeTypesSaneDefaultsAttributesDetails
    target_org: GetDescribeTypesSaneDefaultsAttributesDetails
    target_location: GetDescribeTypesSaneDefaultsAttributesDetails
    target_external: GetDescribeTypesSaneDefaultsAttributesDetails
    btc: GetDescribeTypesSaneDefaultsAttributesDetails
    dash: GetDescribeTypesSaneDefaultsAttributesDetails
    xmr: GetDescribeTypesSaneDefaultsAttributesDetails
    iban: GetDescribeTypesSaneDefaultsAttributesDetails
    bic: GetDescribeTypesSaneDefaultsAttributesDetails
    bank_account_nr: GetDescribeTypesSaneDefaultsAttributesDetails
    aba_rtn: GetDescribeTypesSaneDefaultsAttributesDetails
    bin: GetDescribeTypesSaneDefaultsAttributesDetails
    cc_number: GetDescribeTypesSaneDefaultsAttributesDetails
    prtn: GetDescribeTypesSaneDefaultsAttributesDetails
    phone_number: GetDescribeTypesSaneDefaultsAttributesDetails
    threat_actor: GetDescribeTypesSaneDefaultsAttributesDetails
    campaign_name: GetDescribeTypesSaneDefaultsAttributesDetails
    campaign_id: GetDescribeTypesSaneDefaultsAttributesDetails
    malware_type: GetDescribeTypesSaneDefaultsAttributesDetails
    uri: GetDescribeTypesSaneDefaultsAttributesDetails
    authentihash: GetDescribeTypesSaneDefaultsAttributesDetails
    vhash: GetDescribeTypesSaneDefaultsAttributesDetails
    ssdeep: GetDescribeTypesSaneDefaultsAttributesDetails
    imphash: GetDescribeTypesSaneDefaultsAttributesDetails
    telfhash: GetDescribeTypesSaneDefaultsAttributesDetails
    pehash: GetDescribeTypesSaneDefaultsAttributesDetails
    impfuzzy: GetDescribeTypesSaneDefaultsAttributesDetails
    sha224: GetDescribeTypesSaneDefaultsAttributesDetails
    sha384: GetDescribeTypesSaneDefaultsAttributesDetails
    sha512: GetDescribeTypesSaneDefaultsAttributesDetails
    sha512_224: GetDescribeTypesSaneDefaultsAttributesDetails
    sha512_256: GetDescribeTypesSaneDefaultsAttributesDetails
    sha3_224: GetDescribeTypesSaneDefaultsAttributesDetails
    sha3_256: GetDescribeTypesSaneDefaultsAttributesDetails
    sha3_384: GetDescribeTypesSaneDefaultsAttributesDetails
    sha3_512: GetDescribeTypesSaneDefaultsAttributesDetails
    tlsh: GetDescribeTypesSaneDefaultsAttributesDetails
    cdhash: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_authentihash: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_vhash: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_ssdeep: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_imphash: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_impfuzzy: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_pehash: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha224: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha384: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha512: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha512_224: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha512_256: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha3_224: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha3_256: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha3_384: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_sha3_512: GetDescribeTypesSaneDefaultsAttributesDetails
    filename_tlsh: GetDescribeTypesSaneDefaultsAttributesDetails
    windows_scheduled_task: GetDescribeTypesSaneDefaultsAttributesDetails
    windows_service_name: GetDescribeTypesSaneDefaultsAttributesDetails
    windows_service_displayname: GetDescribeTypesSaneDefaultsAttributesDetails
    whois_registrant_email: GetDescribeTypesSaneDefaultsAttributesDetails
    whois_registrant_phone: GetDescribeTypesSaneDefaultsAttributesDetails
    whois_registrant_name: GetDescribeTypesSaneDefaultsAttributesDetails
    whois_registrant_org: GetDescribeTypesSaneDefaultsAttributesDetails
    whois_registrar: GetDescribeTypesSaneDefaultsAttributesDetails
    whois_creation_date: GetDescribeTypesSaneDefaultsAttributesDetails
    x509_fingerprint_sha1: GetDescribeTypesSaneDefaultsAttributesDetails
    x509_fingerprint_md5: GetDescribeTypesSaneDefaultsAttributesDetails
    x509_fingerprint_sha256: GetDescribeTypesSaneDefaultsAttributesDetails
    dns_soa_email: GetDescribeTypesSaneDefaultsAttributesDetails
    size_in_bytes: GetDescribeTypesSaneDefaultsAttributesDetails
    counter: GetDescribeTypesSaneDefaultsAttributesDetails
    datetime: GetDescribeTypesSaneDefaultsAttributesDetails
    port: GetDescribeTypesSaneDefaultsAttributesDetails
    ip_dst_port: GetDescribeTypesSaneDefaultsAttributesDetails
    ip_src_port: GetDescribeTypesSaneDefaultsAttributesDetails
    hostname_port: GetDescribeTypesSaneDefaultsAttributesDetails
    mac_address: GetDescribeTypesSaneDefaultsAttributesDetails
    mac_eui_64: GetDescribeTypesSaneDefaultsAttributesDetails
    email_dst_display_name: GetDescribeTypesSaneDefaultsAttributesDetails
    email_src_display_name: GetDescribeTypesSaneDefaultsAttributesDetails
    email_header: GetDescribeTypesSaneDefaultsAttributesDetails
    email_reply_to: GetDescribeTypesSaneDefaultsAttributesDetails
    email_x_mailer: GetDescribeTypesSaneDefaultsAttributesDetails
    email_mime_boundary: GetDescribeTypesSaneDefaultsAttributesDetails
    email_thread_index: GetDescribeTypesSaneDefaultsAttributesDetails
    email_message_id: GetDescribeTypesSaneDefaultsAttributesDetails
    github_username: GetDescribeTypesSaneDefaultsAttributesDetails
    github_repository: GetDescribeTypesSaneDefaultsAttributesDetails
    github_organisation: GetDescribeTypesSaneDefaultsAttributesDetails
    jabber_id: GetDescribeTypesSaneDefaultsAttributesDetails
    twitter_id: GetDescribeTypesSaneDefaultsAttributesDetails
    dkim: GetDescribeTypesSaneDefaultsAttributesDetails
    dkim_signature: GetDescribeTypesSaneDefaultsAttributesDetails
    first_name: GetDescribeTypesSaneDefaultsAttributesDetails
    middle_name: GetDescribeTypesSaneDefaultsAttributesDetails
    last_name: GetDescribeTypesSaneDefaultsAttributesDetails
    full_name: GetDescribeTypesSaneDefaultsAttributesDetails
    date_of_birth: GetDescribeTypesSaneDefaultsAttributesDetails
    place_of_birth: GetDescribeTypesSaneDefaultsAttributesDetails
    gender: GetDescribeTypesSaneDefaultsAttributesDetails
    passport_number: GetDescribeTypesSaneDefaultsAttributesDetails
    passport_country: GetDescribeTypesSaneDefaultsAttributesDetails
    passport_expiration: GetDescribeTypesSaneDefaultsAttributesDetails
    redress_number: GetDescribeTypesSaneDefaultsAttributesDetails
    nationality: GetDescribeTypesSaneDefaultsAttributesDetails
    visa_number: GetDescribeTypesSaneDefaultsAttributesDetails
    issue_date_of_the_visa: GetDescribeTypesSaneDefaultsAttributesDetails
    primary_residence: GetDescribeTypesSaneDefaultsAttributesDetails
    country_of_residence: GetDescribeTypesSaneDefaultsAttributesDetails
    special_service_request: GetDescribeTypesSaneDefaultsAttributesDetails
    frequent_flyer_number: GetDescribeTypesSaneDefaultsAttributesDetails
    travel_details: GetDescribeTypesSaneDefaultsAttributesDetails
    payment_details: GetDescribeTypesSaneDefaultsAttributesDetails
    place_port_of_original_embarkation: GetDescribeTypesSaneDefaultsAttributesDetails
    place_port_of_clearance: GetDescribeTypesSaneDefaultsAttributesDetails
    place_port_of_onward_foreign_destination: GetDescribeTypesSaneDefaultsAttributesDetails
    passenger_name_record_locator_number: GetDescribeTypesSaneDefaultsAttributesDetails
    mobile_application_id: GetDescribeTypesSaneDefaultsAttributesDetails
    azure_application_id: GetDescribeTypesSaneDefaultsAttributesDetails
    chrome_extension_id: GetDescribeTypesSaneDefaultsAttributesDetails
    cortex: GetDescribeTypesSaneDefaultsAttributesDetails
    boolean: GetDescribeTypesSaneDefaultsAttributesDetails
    anonymised: GetDescribeTypesSaneDefaultsAttributesDetails


class GetDescribeTypesSaneDefaults(BaseModel):
    sane_defaults: GetDescribeTypesSaneDefaultsAttributes


class GetDescribeTypesTypes(BaseModel):
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


class GetDescribeTypesCategories(BaseModel):
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


class GetDescribeTypesCategoryTypeMappings(BaseModel):
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


class GetDescribeTypesDescribeTypesAttributes(BaseModel):
    sane_defaults: GetDescribeTypesSaneDefaults
    types: GetDescribeTypesTypes
    categories: GetDescribeTypesCategories
    category_type_mappings: GetDescribeTypesCategoryTypeMappings


class GetDescribeTypesResponse(BaseModel):
    result: GetDescribeTypesDescribeTypesAttributes

    class Config:
        orm_mode = True
