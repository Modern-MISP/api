from pydantic import BaseModel


class GetDescribeTypesSaneDefaultsAttributes(BaseModel):
    default_category: str
    to_ids: int


class GetDescribeTypesSaneDefaults(BaseModel):
    md5: GetDescribeTypesSaneDefaultsAttributes
    sha1: GetDescribeTypesSaneDefaultsAttributes
    sha256: GetDescribeTypesSaneDefaultsAttributes
    filename: GetDescribeTypesSaneDefaultsAttributes
    pdb: GetDescribeTypesSaneDefaultsAttributes
    filename_md5: GetDescribeTypesSaneDefaultsAttributes
    filename_sha1: GetDescribeTypesSaneDefaultsAttributes
    filename_sha256: GetDescribeTypesSaneDefaultsAttributes
    ip_src: GetDescribeTypesSaneDefaultsAttributes
    ip_dst: GetDescribeTypesSaneDefaultsAttributes
    hostname: GetDescribeTypesSaneDefaultsAttributes
    domain: GetDescribeTypesSaneDefaultsAttributes
    domain_ip: GetDescribeTypesSaneDefaultsAttributes
    email: GetDescribeTypesSaneDefaultsAttributes
    email_src: GetDescribeTypesSaneDefaultsAttributes
    eppn: GetDescribeTypesSaneDefaultsAttributes
    email_dst: GetDescribeTypesSaneDefaultsAttributes
    email_subject: GetDescribeTypesSaneDefaultsAttributes
    email_attachment: GetDescribeTypesSaneDefaultsAttributes
    email_body: GetDescribeTypesSaneDefaultsAttributes
    float: GetDescribeTypesSaneDefaultsAttributes
    git_commit_id: GetDescribeTypesSaneDefaultsAttributes
    url: GetDescribeTypesSaneDefaultsAttributes
    http_method: GetDescribeTypesSaneDefaultsAttributes
    user_agent: GetDescribeTypesSaneDefaultsAttributes
    ja3_fingerprint_md5: GetDescribeTypesSaneDefaultsAttributes
    jarm_fingerprint: GetDescribeTypesSaneDefaultsAttributes
    favicon_mmh3: GetDescribeTypesSaneDefaultsAttributes
    hassh_md5: GetDescribeTypesSaneDefaultsAttributes
    hasshserver_md5: GetDescribeTypesSaneDefaultsAttributes
    regkey: GetDescribeTypesSaneDefaultsAttributes
    regkey_value: GetDescribeTypesSaneDefaultsAttributes
    AS: GetDescribeTypesSaneDefaultsAttributes
    snort: GetDescribeTypesSaneDefaultsAttributes
    bro: GetDescribeTypesSaneDefaultsAttributes
    zeek: GetDescribeTypesSaneDefaultsAttributes
    community_id: GetDescribeTypesSaneDefaultsAttributes
    pattern_in_file: GetDescribeTypesSaneDefaultsAttributes
    pattern_in_traffic: GetDescribeTypesSaneDefaultsAttributes
    pattern_in_memory: GetDescribeTypesSaneDefaultsAttributes
    filename_pattern: GetDescribeTypesSaneDefaultsAttributes
    pgp_public_key: GetDescribeTypesSaneDefaultsAttributes
    pgp_private_key: GetDescribeTypesSaneDefaultsAttributes
    ssh_fingerprint: GetDescribeTypesSaneDefaultsAttributes
    yara: GetDescribeTypesSaneDefaultsAttributes
    stix2_pattern: GetDescribeTypesSaneDefaultsAttributes
    sigma: GetDescribeTypesSaneDefaultsAttributes
    gene: GetDescribeTypesSaneDefaultsAttributes
    kusto_query: GetDescribeTypesSaneDefaultsAttributes
    mime_type: GetDescribeTypesSaneDefaultsAttributes
    identity_card_number: GetDescribeTypesSaneDefaultsAttributes
    cookie: GetDescribeTypesSaneDefaultsAttributes
    vulnerability: GetDescribeTypesSaneDefaultsAttributes
    cpe: GetDescribeTypesSaneDefaultsAttributes
    weakness: GetDescribeTypesSaneDefaultsAttributes
    attachment: GetDescribeTypesSaneDefaultsAttributes
    malware_sample: GetDescribeTypesSaneDefaultsAttributes
    link: GetDescribeTypesSaneDefaultsAttributes
    comment: GetDescribeTypesSaneDefaultsAttributes
    text: GetDescribeTypesSaneDefaultsAttributes
    hex: GetDescribeTypesSaneDefaultsAttributes
    other: GetDescribeTypesSaneDefaultsAttributes
    named_pipe: GetDescribeTypesSaneDefaultsAttributes
    mutex: GetDescribeTypesSaneDefaultsAttributes
    process_state: GetDescribeTypesSaneDefaultsAttributes
    target_user: GetDescribeTypesSaneDefaultsAttributes
    target_email: GetDescribeTypesSaneDefaultsAttributes
    target_machine: GetDescribeTypesSaneDefaultsAttributes
    target_org: GetDescribeTypesSaneDefaultsAttributes
    target_location: GetDescribeTypesSaneDefaultsAttributes
    target_external: GetDescribeTypesSaneDefaultsAttributes
    btc: GetDescribeTypesSaneDefaultsAttributes
    dash: GetDescribeTypesSaneDefaultsAttributes
    xmr: GetDescribeTypesSaneDefaultsAttributes
    iban: GetDescribeTypesSaneDefaultsAttributes
    bic: GetDescribeTypesSaneDefaultsAttributes
    bank_account_nr: GetDescribeTypesSaneDefaultsAttributes
    aba_rtn: GetDescribeTypesSaneDefaultsAttributes
    bin: GetDescribeTypesSaneDefaultsAttributes
    cc_number: GetDescribeTypesSaneDefaultsAttributes
    prtn: GetDescribeTypesSaneDefaultsAttributes
    phone_number: GetDescribeTypesSaneDefaultsAttributes
    threat_actor: GetDescribeTypesSaneDefaultsAttributes
    campaign_name: GetDescribeTypesSaneDefaultsAttributes
    campaign_id: GetDescribeTypesSaneDefaultsAttributes
    malware_type: GetDescribeTypesSaneDefaultsAttributes
    uri: GetDescribeTypesSaneDefaultsAttributes
    authentihash: GetDescribeTypesSaneDefaultsAttributes
    vhash: GetDescribeTypesSaneDefaultsAttributes
    ssdeep: GetDescribeTypesSaneDefaultsAttributes
    imphash: GetDescribeTypesSaneDefaultsAttributes
    telfhash: GetDescribeTypesSaneDefaultsAttributes
    pehash: GetDescribeTypesSaneDefaultsAttributes
    impfuzzy: GetDescribeTypesSaneDefaultsAttributes
    sha224: GetDescribeTypesSaneDefaultsAttributes
    sha384: GetDescribeTypesSaneDefaultsAttributes
    sha512: GetDescribeTypesSaneDefaultsAttributes
    sha512_224: GetDescribeTypesSaneDefaultsAttributes
    sha512_256: GetDescribeTypesSaneDefaultsAttributes
    sha3_224: GetDescribeTypesSaneDefaultsAttributes
    sha3_256: GetDescribeTypesSaneDefaultsAttributes
    sha3_384: GetDescribeTypesSaneDefaultsAttributes
    sha3_512: GetDescribeTypesSaneDefaultsAttributes
    tlsh: GetDescribeTypesSaneDefaultsAttributes
    cdhash: GetDescribeTypesSaneDefaultsAttributes
    filename_authentihash: GetDescribeTypesSaneDefaultsAttributes
    filename_vhash: GetDescribeTypesSaneDefaultsAttributes
    filename_ssdeep: GetDescribeTypesSaneDefaultsAttributes
    filename_imphash: GetDescribeTypesSaneDefaultsAttributes
    filename_impfuzzy: GetDescribeTypesSaneDefaultsAttributes
    filename_pehash: GetDescribeTypesSaneDefaultsAttributes
    filename_sha224: GetDescribeTypesSaneDefaultsAttributes
    filename_sha384: GetDescribeTypesSaneDefaultsAttributes
    filename_sha512: GetDescribeTypesSaneDefaultsAttributes
    filename_sha512_224: GetDescribeTypesSaneDefaultsAttributes
    filename_sha512_256: GetDescribeTypesSaneDefaultsAttributes
    filename_sha3_224: GetDescribeTypesSaneDefaultsAttributes
    filename_sha3_256: GetDescribeTypesSaneDefaultsAttributes
    filename_sha3_384: GetDescribeTypesSaneDefaultsAttributes
    filename_sha3_512: GetDescribeTypesSaneDefaultsAttributes
    filename_tlsh: GetDescribeTypesSaneDefaultsAttributes
    windows_scheduled_task: GetDescribeTypesSaneDefaultsAttributes
    windows_service_name: GetDescribeTypesSaneDefaultsAttributes
    windows_service_displayname: GetDescribeTypesSaneDefaultsAttributes
    whois_registrant_email: GetDescribeTypesSaneDefaultsAttributes
    whois_registrant_phone: GetDescribeTypesSaneDefaultsAttributes
    whois_registrant_name: GetDescribeTypesSaneDefaultsAttributes
    whois_registrant_org: GetDescribeTypesSaneDefaultsAttributes
    whois_registrar: GetDescribeTypesSaneDefaultsAttributes
    whois_creation_date: GetDescribeTypesSaneDefaultsAttributes
    x509_fingerprint_sha1: GetDescribeTypesSaneDefaultsAttributes
    x509_fingerprint_md5: GetDescribeTypesSaneDefaultsAttributes
    x509_fingerprint_sha256: GetDescribeTypesSaneDefaultsAttributes
    dns_soa_email: GetDescribeTypesSaneDefaultsAttributes
    size_in_bytes: GetDescribeTypesSaneDefaultsAttributes
    counter: GetDescribeTypesSaneDefaultsAttributes
    datetime: GetDescribeTypesSaneDefaultsAttributes
    port: GetDescribeTypesSaneDefaultsAttributes
    ip_dst_port: GetDescribeTypesSaneDefaultsAttributes
    ip_src_port: GetDescribeTypesSaneDefaultsAttributes
    hostname_port: GetDescribeTypesSaneDefaultsAttributes
    mac_address: GetDescribeTypesSaneDefaultsAttributes
    mac_eui_64: GetDescribeTypesSaneDefaultsAttributes
    email_dst_display_name: GetDescribeTypesSaneDefaultsAttributes
    email_src_display_name: GetDescribeTypesSaneDefaultsAttributes
    email_header: GetDescribeTypesSaneDefaultsAttributes
    email_reply_to: GetDescribeTypesSaneDefaultsAttributes
    email_x_mailer: GetDescribeTypesSaneDefaultsAttributes
    email_mime_boundary: GetDescribeTypesSaneDefaultsAttributes
    email_thread_index: GetDescribeTypesSaneDefaultsAttributes
    email_message_id: GetDescribeTypesSaneDefaultsAttributes
    github_username: GetDescribeTypesSaneDefaultsAttributes
    github_repository: GetDescribeTypesSaneDefaultsAttributes
    github_organisation: GetDescribeTypesSaneDefaultsAttributes
    jabber_id: GetDescribeTypesSaneDefaultsAttributes
    twitter_id: GetDescribeTypesSaneDefaultsAttributes
    dkim: GetDescribeTypesSaneDefaultsAttributes
    dkim_signature: GetDescribeTypesSaneDefaultsAttributes
    first_name: GetDescribeTypesSaneDefaultsAttributes
    middle_name: GetDescribeTypesSaneDefaultsAttributes
    last_name: GetDescribeTypesSaneDefaultsAttributes
    full_name: GetDescribeTypesSaneDefaultsAttributes
    date_of_birth: GetDescribeTypesSaneDefaultsAttributes
    place_of_birth: GetDescribeTypesSaneDefaultsAttributes
    gender: GetDescribeTypesSaneDefaultsAttributes
    passport_number: GetDescribeTypesSaneDefaultsAttributes
    passport_country: GetDescribeTypesSaneDefaultsAttributes
    passport_expiration: GetDescribeTypesSaneDefaultsAttributes
    redress_number: GetDescribeTypesSaneDefaultsAttributes
    nationality: GetDescribeTypesSaneDefaultsAttributes
    visa_number: GetDescribeTypesSaneDefaultsAttributes
    issue_date_of_the_visa: GetDescribeTypesSaneDefaultsAttributes
    primary_residence: GetDescribeTypesSaneDefaultsAttributes
    country_of_residence: GetDescribeTypesSaneDefaultsAttributes
    special_service_request: GetDescribeTypesSaneDefaultsAttributes
    frequent_flyer_number: GetDescribeTypesSaneDefaultsAttributes
    travel_details: GetDescribeTypesSaneDefaultsAttributes
    payment_details: GetDescribeTypesSaneDefaultsAttributes
    place_port_of_original_embarkation: GetDescribeTypesSaneDefaultsAttributes
    place_port_of_clearance: GetDescribeTypesSaneDefaultsAttributes
    place_port_of_onward_foreign_destination: GetDescribeTypesSaneDefaultsAttributes
    passenger_name_record_locator_number: GetDescribeTypesSaneDefaultsAttributes
    mobile_application_id: GetDescribeTypesSaneDefaultsAttributes
    azure_application_id: GetDescribeTypesSaneDefaultsAttributes
    chrome_extension_id: GetDescribeTypesSaneDefaultsAttributes
    cortex: GetDescribeTypesSaneDefaultsAttributes
    boolean: GetDescribeTypesSaneDefaultsAttributes
    anonymised: GetDescribeTypesSaneDefaultsAttributes


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
