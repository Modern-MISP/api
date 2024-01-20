from pydantic import BaseModel, Field
from typing_extensions import Annotated


class GetDescribeTypesSaneDefaultsAttributes(BaseModel):
    default_category: str
    to_ids: int


class GetDescribeTypesSaneDefaults(BaseModel):
    MD5: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="md5")
    ] = GetDescribeTypesSaneDefaultsAttributes(
        default_category="Payload delivery", to_ids=1
    )
    SHA1: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha1")
    ] = GetDescribeTypesSaneDefaultsAttributes(
        default_category="Payload delivery", to_ids=1
    )
    SHA256: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha256")
    ] = GetDescribeTypesSaneDefaultsAttributes(
        default_category="Payload delivery", to_ids=1
    )
    FILENAME: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename")]
    PDB: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|md5")]
    FILENAME_MD5: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="pdb")]
    FILENAME_SHA1: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha1")
    ]
    FILENAME_SHA256: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha256")
    ]
    IP_SRC: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="ip-src")]
    IP_DST: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="ip-dst")]
    HOSTNAME: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="hostname")]
    DOMAIN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="domain")]
    DOMAIN_IP: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="domain|ip")
    ]
    EMAIL: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="email")]
    EMAIL_SRC: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-src")
    ]
    EPPN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="eppn")]
    EMAIL_DST: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-dst")
    ]
    EMAIL_SUBJECT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-subject")
    ]
    EMAIL_ATTACHMENT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-attachment")
    ]
    EMAIL_BODY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-body")
    ]
    FLOAT: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="float")]
    GIT_COMMIT_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="git-commit-id")
    ]
    URL: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="url")]
    HTTP_METHOD: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="http-method")
    ]
    USER_AGENT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="user-agent")
    ]
    JA3_FINGERPRINT_MD5: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="ja3-fingerprint-md5")
    ]
    JARM_FINGERPRINT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="jarm-fingerprint")
    ]
    FAVICON_MMH3: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="favicon-mmh3")
    ]
    HASSH_MD5: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="hassh-md5")
    ]
    HASSHSERVER_MD5: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="hasshserver-md5")
    ]
    REGKEY: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="regkey")]
    REGKEY_VALUE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="regkey|value")
    ]
    AS: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="AS")]
    SNORT: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="snort")]
    BRO: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="bro")]
    ZEEK: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="zeek")]
    COMMUNITY_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="community-id")
    ]
    PATTERN_IN_FILE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="pattern-in-file")
    ]
    PATTERN_IN_TRAFFIC: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="pattern-in-traffic")
    ]
    PATTERN_IN_MEMORY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="pattern-in-memory")
    ]
    FILENAME_PATTERN: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename-pattern")
    ]
    PGP_PUBLIC_KEY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="pgp-public-key")
    ]
    PGP_PRIVATE_KEY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="pgp-private-key")
    ]
    SSH_FINGERPRINT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="ssh-fingerprint")
    ]
    YARA: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="yara")]
    STIX2_PATTERN: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="stix2-pattern")
    ]
    SIGMA: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sigma")]
    GENE: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="gene")]
    KUSTO_QUERY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="kusto-query")
    ]
    MIME_TYPE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="mime-type")
    ]
    IDENTITY_CARD_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="identity-card-number")
    ]
    COOKIE: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="cookie")]
    VULNERABILITY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="vulnerability")
    ]
    CPE: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="cpe")]
    WEAKNESS: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="weakness")]
    ATTACHMENT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="attachment")
    ]
    MALWARE_SAMPLE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="malware-sample")
    ]
    LINK: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="link")]
    COMMENT: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="comment")]
    TEXT: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="text")]
    HEX: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="hex")]
    OTHER: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="other")]
    NAMED_PIPE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="named pipe")
    ]
    MUTEX: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="mutex")]
    PROCESS_STATE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="process-state")
    ]
    TARGET_USER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="target-user")
    ]
    TARGET_EMAIL: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="target-email")
    ]
    TARGET_MACHINE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="target-machine")
    ]
    TARGET_ORG: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="target-org")
    ]
    TARGET_LOCATION: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="target-location")
    ]
    TARGET_EXTERNAL: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="target-external")
    ]
    BTC: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="btc")]
    DASH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="dash")]
    XMR: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="xmr")]
    IBAN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="iban")]
    BIC: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="bic")]
    BANK_ACCOUNT_NR: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="bank-account-nr")
    ]
    ABA_RTN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="aba-rtn")]
    BIN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="bin")]
    CC_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="cc-number")
    ]
    PRTN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="prtn")]
    PHONE_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="phone-number")
    ]
    THREAT_ACTOR: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="threat-actor")
    ]
    CAMPAIGN_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="campaign-name")
    ]
    CAMPAIGN_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="campaign-id")
    ]
    MALWARE_TYPE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="malware-type")
    ]
    URI: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="uri")]
    AUTHENTIHASH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="authentihash")
    ]
    VHASH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="vhash")]
    SSDEEP: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="ssdeep")]
    IMPHASH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="imphash")]
    TELFHASH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="telfhash")]
    PEHASH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="pehash")]
    IMPFUZZY: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="impfuzzy")]
    SHA224: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha224")]
    SHA384: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha384")]
    SHA512: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha512")]
    SHA512_224: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha512/224")
    ]
    SHA512_256: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha512/256")
    ]
    SHA3_224: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha3-224")]
    SHA3_256: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha3-256")]
    SHA3_384: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha3-384")]
    SHA3_512: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="sha3-512")]
    TLSH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="tlsh")]
    CDHASH: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="cdhash")]
    FILENAME_AUTHENTIHASH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|authentihash")
    ]
    FILENAME_VHASH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|vhash")
    ]
    FILENAME_SSDEEP: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|ssdeep")
    ]
    FILENAME_IMPHASH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|imphash")
    ]
    FILENAME_IMPFUZZY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|impfuzzy")
    ]
    FILENAME_PEHASH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|pehash")
    ]
    FILENAME_SHA224: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha224")
    ]
    FILENAME_SHA384: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha384")
    ]
    FILENAME_SHA512: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha512")
    ]
    FILENAME_SHA512_224: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha512/224")
    ]
    FILENAME_SHA512_256: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha512/256")
    ]
    FILENAME_SHA3_224: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha3-224")
    ]
    FILENAME_SHA3_256: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha3-256")
    ]
    FILENAME_SHA3_384: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha3-384")
    ]
    FILENAME_SHA3_512: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|sha3-512")
    ]
    FILENAME_TLSH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="filename|tlsh")
    ]
    WINDOWS_SCHEDULED_TASK: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="windows-scheduled-task")
    ]
    WINDOWS_SERVICE_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="windows-service-name")
    ]
    WINDOWS_SERVICE_DISPLAYNAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes,
        Field(alias="windows-service-displayname"),
    ]
    WHOIS_REGISTRANT_EMAIL: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="whois-registrant-email")
    ]
    WHOIS_REGISTRANT_PHONE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="whois-registrant-phone")
    ]
    WHOIS_REGISTRANT_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="whois-registrant-name")
    ]
    WHOIS_REGISTRANT_ORG: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="whois-registrant-org")
    ]
    WHOIS_REGISTRAR: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="whois-registrar")
    ]
    WHOIS_CREATION_DATE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="whois-creation-date")
    ]
    X509_FINGERPRINT_SHA1: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="x509-fingerprint-sha1")
    ]
    X509_FINGERPRINT_MD5: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="x509-fingerprint-md5")
    ]
    X509_FINGERPRINT_SHA256: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="x509-fingerprint-sha256")
    ]
    DNS_SOA_EMAIL: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="dns-soa-email")
    ]
    SIZE_IN_BYTES: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="size-in-bytes")
    ]
    COUNTER: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="counter")]
    DATETIME: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="datetime")]
    PORT: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="port")]
    IP_DST_PORT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="ip-dst|port")
    ]
    IP_SRC_PORT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="ip-src|port")
    ]
    HOSTNAME_PORT: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="hostname|port")
    ]
    MAC_ADDRESS: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="mac-address")
    ]
    MAC_EUI_64: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="mac-eui-64")
    ]
    EMAIL_DST_DISPLAY_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-dst-display-name")
    ]
    EMAIL_SRC_DISPLAY_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-src-display-name")
    ]
    EMAIL_HEADER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-header")
    ]
    EMAIL_REPLY_TO: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-reply-to")
    ]
    EMAIL_X_MAILER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-x-mailer")
    ]
    EMAIL_MIME_BOUNDARY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-mime-boundary")
    ]
    EMAIL_THREAD_INDEX: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-thread-index")
    ]
    EMAIL_MESSAGE_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="email-message-id")
    ]
    GITHUB_USERNAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="github-username")
    ]
    GITHUB_REPOSITORY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="github-repository")
    ]
    GITHUB_ORGANISATION: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="github-organisation")
    ]
    JABBER_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="jabber-id")
    ]
    TWITTER_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="twitter-id")
    ]
    DKIM: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="dkim")]
    DKIM_SIGNATURE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="dkim-signature")
    ]
    FIRST_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="first-name")
    ]
    MIDDLE_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="middle-name")
    ]
    LAST_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="last-name")
    ]
    FULL_NAME: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="full-name")
    ]
    DATE_OF_BIRTH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="date-of-birth")
    ]
    PLACE_OF_BIRTH: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="place-of-birth")
    ]
    GENDER: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="gender")]
    PASSPORT_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="passport-number")
    ]
    PASSPORT_COUNTRY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="passport-country")
    ]
    PASSPORT_EXPIRATION: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="passport-expiration")
    ]
    REDRESS_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="redress-number")
    ]
    NATIONALITY: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="nationality")
    ]
    VISA_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="visa-number")
    ]
    ISSUE_DATE_OF_THE_VISA: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="issue-date-of-the-visa")
    ]
    PRIMARY_RESIDENCE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="primary-residence")
    ]
    COUNTRY_OF_RESIDENCE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="country-of-residence")
    ]
    SPECIAL_SERVICE_REQUEST: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="special-service-request")
    ]
    FREQUENT_FLYER_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="frequent-flyer-number")
    ]
    TRAVEL_DETAILS: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="travel-details")
    ]
    PAYMENT_DETAILS: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="payment-details")
    ]
    PLACE_PORT_OF_ORIGINAL_EMBARKATION: Annotated[
        GetDescribeTypesSaneDefaultsAttributes,
        Field(alias="place-port-of-original-embarkation"),
    ]
    PLACE_PORT_OF_CLEARANCE: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="place-port-of-clearance")
    ]
    PLACE_PORT_OF_ONWARD_FOREIGN_DESTINATION: Annotated[
        GetDescribeTypesSaneDefaultsAttributes,
        Field(alias="place-port-of-onward-foreign-destination"),
    ]
    PASSENGER_NAME_RECORD_LOCATOR_NUMBER: Annotated[
        GetDescribeTypesSaneDefaultsAttributes,
        Field(alias="passenger-name-record-locator-number"),
    ]
    MOBILE_APPLICATION_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="mobile-application-id")
    ]
    AZURE_APPLICATION_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="azure-application-id")
    ]
    CHROME_EXTENSION_ID: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="chrome-extension-id")
    ]
    CORTEX: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="cortex")]
    BOOLEAN: Annotated[GetDescribeTypesSaneDefaultsAttributes, Field(alias="boolean")]
    ANONYMISED: Annotated[
        GetDescribeTypesSaneDefaultsAttributes, Field(alias="anonymised")
    ]


class GetDescribeTypesCategoryTypeMappings(BaseModel):
    INTERNAL_REFERENCE: Annotated[list[str], Field(alias="Internal reference")] = [
        "text",
        "link",
        "comment",
        "other",
        "hex",
        "anonymised",
        "git-commit-id",
    ]
    TARGETING_DATA: Annotated[list[str], Field(alias="Targeting data")] = [
        "target-user",
        "target-email",
        "target-machine",
        "target-org",
        "target-location",
        "target-external",
        "comment",
        "anonymised",
    ]
    ANTIVIRUS_DETECTION: Annotated[list[str], Field(alias="Antivirus detection")] = [
        "link",
        "comment",
        "text",
        "hex",
        "attachment",
        "other",
        "anonymised",
    ]
    PAYLOAD_DELIVERY: Annotated[list[str], Field(alias="Payload delivery")] = [
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
    ARTIFACTS_DROPPED: Annotated[list[str], Field(alias="Artifacts dropped")] = [
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
    PAYLOAD_INSTALLATION: Annotated[list[str], Field(alias="Payload installation")] = [
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
    PERSISTENCE_MECHANISM: Annotated[
        list[str], Field(alias="Persistence mechanism")
    ] = [
        "filename",
        "regkey",
        "regkey|value",
        "comment",
        "text",
        "other",
        "hex",
        "anonymised",
    ]
    NETWORK_ACTIVITY: Annotated[list[str], Field(alias="Network activity")] = [
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
    PAYLOAD_TYPE: Annotated[list[str], Field(alias="Payload type")] = [
        "comment",
        "text",
        "other",
        "anonymised",
    ]
    ATTRIBUTION: Annotated[list[str], Field(alias="Attribution")] = [
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
    EXTERNAL_ANALYSIS: Annotated[list[str], Field(alias="External analysis")] = [
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
    FINANCIAL_FRAUD: Annotated[list[str], Field(alias="Financial fraud")] = [
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
    SUPPORT_TOOL: Annotated[list[str], Field(alias="Support tool")] = [
        "link",
        "text",
        "attachment",
        "comment",
        "other",
        "hex",
        "anonymised",
    ]
    SOCIAL_NETWORK: Annotated[list[str], Field(alias="Social network")] = [
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
    PERSON: Annotated[list[str], Field(alias="Person")] = [
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
    OTHER: Annotated[list[str], Field(alias="Other")] = [
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
    SANE_DEFAULTS: Annotated[GetDescribeTypesSaneDefaults, Field(alias="sane_defaults")]
    TYPES: Annotated[list[str], Field(alias="types")] = [
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
    CATEGORIES: Annotated[list[str], Field(alias="categories")] = [
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
    CATEGORY_TYPE_MAPPINGS: Annotated[
        GetDescribeTypesCategoryTypeMappings, Field(alias="category_type_mappings")
    ]


class GetDescribeTypesResponse(BaseModel):
    result: GetDescribeTypesDescribeTypesAttributes

    class Config:
        orm_mode = True
