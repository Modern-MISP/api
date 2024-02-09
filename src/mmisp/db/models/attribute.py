from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base
from .event import Event
from .object import Object
from .sharing_group import SharingGroup
from .tag import Tag


class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    event_id = Column(Integer, ForeignKey(Event.id), index=True, nullable=False)
    object_id = Column(Integer, ForeignKey(Object.id), index=True, nullable=False, default=0)
    object_relation = Column(String(255), index=True)
    category = Column(String(255), index=True, nullable=False)
    type = Column(String(255), index=True, nullable=False)
    value = Column(String(255), index=True, nullable=False, default=None)
    value1 = Column(String(255), index=True, nullable=False, default=None)
    value2 = Column(String(255), index=True, nullable=False, default=None)
    to_ids = Column(Boolean, nullable=False, default=True)
    timestamp = Column(Integer, nullable=False, default=0)
    distribution = Column(Integer, nullable=False, default=0)
    sharing_group_id = Column(Integer, ForeignKey(SharingGroup.id), index=True, nullable=False)
    comment = Column(String(255))
    deleted = Column(Boolean, nullable=False, default=False)
    disable_correlation = Column(Boolean, nullable=False, default=False)
    first_seen = Column(Integer, index=True, nullable=True)
    last_seen = Column(Integer, index=True, nullable=True)
    event_uuid = Column(String(255), ForeignKey(Event.uuid))  # new

    # tags = relationship("AttributeTag")


class AttributeTag(Base):
    __tablename__ = "attribute_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(255), unique=True, default=uuid)
    attribute_id = Column(Integer, ForeignKey(Attribute.id), nullable=False, index=True)
    object_id = Column(Integer, ForeignKey(Object.id), index=True, nullable=False, default=0)
    tag_id = Column(Integer, ForeignKey(Tag.id), nullable=False, index=True)
    local = Column(Boolean, nullable=False, default=False)

    # todo: are the following entries actually needed?
    # id = Column(Integer, primary_key=True)
    # name = Column(String(255))
    # colour = Column(String(255))
    # exportable = Column(Boolean)
    # user_id = Column(String(255))
    # hide_tag = Column(Boolean)
    # numerical_value = Column(Integer)
    # is_galaxy = Column(Boolean)
    # is_costum_galaxy = Column(Boolean)
    # local_only = Column(Boolean)


class AttributeMD5(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "md5"}


class AttributeSHA1(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha1"}


class AttributeSHA256(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha256"}


class AttributeFILENAME(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Persistence mechanism",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename"}


class AttributePDB(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "pdb"}


class AttributeFILENAME_MD5(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|md5"}


class AttributeFILENAME_SHA1(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha1"}


class AttributeFILENAME_SHA256(Attribute):
    default_category = "Payload delivery"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha256"}


class AttributeIP_SRC(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "ip-src"}


class AttributeIP_DST(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "ip-dst"}


class AttributeHOSTNAME(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "hostname"}


class AttributeDOMAIN(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "domain"}


class AttributeDOMAIN_IP(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "domain|ip"}


class AttributeEMAIL(Attribute):
    default_category = "Social network"
    categories = ["Payload delivery", "Network activity", "Attribution", "Social network", "Person"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "email"}


class AttributeEMAIL_SRC(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Network activity", "Social network"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "email-src"}


class AttributeEPPN(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "Social network"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "eppn"}


class AttributeEMAIL_DST(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "Social network"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "email-dst"}


class AttributeEMAIL_SUBJECT(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Network activity"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-subject"}


class AttributeEMAIL_ATTACHMENT(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "email-attachment"}


class AttributeEMAIL_BODY(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-body"}


class AttributeFLOAT(Attribute):
    default_category = "Other"
    categories = ["Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "float"}


class AttributeGIT_COMMIT_ID(Attribute):
    default_category = "Internal reference"
    categories = ["Internal reference"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "git-commit-id"}


class AttributeURL(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "url"}


class AttributeHTTP_METHOD(Attribute):
    default_category = "Network activity"
    categories = ["Network activity"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "http-method"}


class AttributeUSER_AGENT(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "user-agent"}


class AttributeJA3_FINGERPRINT_MD5(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "ja3-fingerprint-md5"}


class AttributeJARM_FINGERPRINT(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "jarm-fingerprint"}


class AttributeFAVICON_MMH3(Attribute):
    default_category = "Network activity"
    categories = ["Network activity"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "favicon-mmh3"}


class AttributeHASSH_MD5(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "hassh-md5"}


class AttributeHASSHSERVER_MD5(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "hasshserver-md5"}


class AttributeREGKEY(Attribute):
    default_category = "Persistence mechanism"
    categories = ["Artifacts dropped", "Persistence mechanism", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "regkey"}


class AttributeREGKEY_VALUE(Attribute):
    default_category = "Persistence mechanism"
    categories = ["Artifacts dropped", "Persistence mechanism", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "regkey|value"}


class AttributeAS(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "AS"}


class AttributeSNORT(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "snort"}


class AttributeBRO(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "bro"}


class AttributeZEEK(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "zeek"}


class AttributeCOMMUNITY_ID(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "community-id"}


class AttributePATTERN_IN_FILE(Attribute):
    default_category = "Payload installation"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Network activity",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "pattern-in-file"}


class AttributePATTERN_IN_TRAFFIC(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Payload installation", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "pattern-in-traffic"}


class AttributePATTERN_IN_MEMORY(Attribute):
    default_category = "Payload installation"
    categories = ["Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "pattern-in-memory"}


class AttributeFILENAME_PATTERN(Attribute):
    default_category = "Payload installation"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Network activity",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename-pattern"}


class AttributePGP_PUBLIC_KEY(Attribute):
    default_category = "Person"
    categories = ["Artifacts dropped", "Social network", "Person", "Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "pgp-public-key"}


class AttributePGP_PRIVATE_KEY(Attribute):
    default_category = "Person"
    categories = ["Artifacts dropped", "Social network", "Person", "Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "pgp-private-key"}


class AttributeSSH_FINGERPRINT(Attribute):
    default_category = "Network activity"
    categories = ["Network activity"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "ssh-fingerprint"}


class AttributeYARA(Attribute):
    default_category = "Payload installation"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "yara"}


class AttributeSTIX2_PATTERN(Attribute):
    default_category = "Payload installation"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "Network activity"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "stix2-pattern"}


class AttributeSIGMA(Attribute):
    default_category = "Payload installation"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sigma"}


class AttributeGENE(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "gene"}


class AttributeKUSTO_QUERY(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "kusto-query"}


class AttributeMIME_TYPE(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "mime-type"}


class AttributeIDENTITY_CARD_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "identity-card-number"}


class AttributeCOOKIE(Attribute):
    default_category = "Network activity"
    categories = ["Artifacts dropped", "Network activity"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "cookie"}


class AttributeVULNERABILITY(Attribute):
    default_category = "External analysis"
    categories = ["Payload delivery", "Payload installation", "External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "vulnerability"}


class AttributeCPE(Attribute):
    default_category = "External analysis"
    categories = ["Payload delivery", "Payload installation", "External analysis", "Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "cpe"}


class AttributeWEAKNESS(Attribute):
    default_category = "External analysis"
    categories = ["Payload delivery", "Payload installation", "External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "weakness"}


class AttributeATTACHMENT(Attribute):
    default_category = "External analysis"
    categories = [
        "Antivirus detection",
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Network activity",
        "External analysis",
        "Support Tool",
    ]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "attachment"}


class AttributeMALWARE_SAMPLE(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "malware-sample"}


class AttributeLINK(Attribute):
    default_category = "External analysis"
    categories = ["Internal reference", "Antivirus detection", "Payload delivery", "External analysis", "Support Tool"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "link"}


class AttributeCOMMENT(Attribute):
    default_category = "Other"
    categories = [
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
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "comment"}


class AttributeTEXT(Attribute):
    default_category = "Other"
    categories = [
        "Internal reference",
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
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "text"}


class AttributeHEX(Attribute):
    default_category = "Other"
    categories = [
        "Internal reference",
        "Antivirus detection",
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Persistence mechanism",
        "Network activity",
        "Financial fraud",
        "Support Tool",
        "Other",
    ]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "hex"}


class AttributeOTHER(Attribute):
    default_category = "Other"
    categories = [
        "Internal reference",
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
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "other"}


class AttributeNAMED_PIPE(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "named pipe"}


class AttributeMUTEX(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "mutex"}


class AttributePROCESS_STATE(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "process-state"}


class AttributeTARGET_USER(Attribute):
    default_category = "Targeting data"
    categories = ["Targeting data"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "target-user"}


class AttributeTARGET_EMAIL(Attribute):
    default_category = "Targeting data"
    categories = ["Targeting data"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "target-email"}


class AttributeTARGET_MACHINE(Attribute):
    default_category = "Targeting data"
    categories = ["Targeting data"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "target-machine"}


class AttributeTARGET_ORG(Attribute):
    default_category = "Targeting data"
    categories = ["Targeting data"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "target-org"}


class AttributeTARGET_LOCATION(Attribute):
    default_category = "Targeting data"
    categories = ["Targeting data"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "target-location"}


class AttributeTARGET_EXTERNAL(Attribute):
    default_category = "Targeting data"
    categories = ["Targeting data"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "target-external"}


class AttributeBTC(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "btc"}


class AttributeDASH(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "dash"}


class AttributeXMR(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "xmr"}


class AttributeIBAN(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "iban"}


class AttributeBIC(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "bic"}


class AttributeBANK_ACCOUNT_NR(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "bank-account-nr"}


class AttributeABA_RTN(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "aba-rtn"}


class AttributeBIN(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "bin"}


class AttributeCC_NUMBER(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "cc-number"}


class AttributePRTN(Attribute):
    default_category = "Financial fraud"
    categories = ["Financial fraud"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "prtn"}


class AttributePHONE_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Financial fraud", "Person", "Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "phone-number"}


class AttributeTHREAT_ACTOR(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "threat-actor"}


class AttributeCAMPAIGN_NAME(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "campaign-name"}


class AttributeCAMPAIGN_ID(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "campaign-id"}


class AttributeMALWARE_TYPE(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Payload installation"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "malware-type"}


class AttributeURI(Attribute):
    default_category = "Network activity"
    categories = ["Network activity"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "uri"}


class AttributeAUTHENTIHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "authentihash"}


class AttributeVHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "vhash"}


class AttributeSSDEEP(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "ssdeep"}


class AttributeIMPHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "imphash"}


class AttributeTELFHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "telfhash"}


class AttributePEHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "pehash"}


class AttributeIMPFUZZY(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "impfuzzy"}


class AttributeSHA224(Attribute):
    default_category = "Payload delivery"
    categories = [""]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha224"}


class AttributeSHA384(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha384"}


class AttributeSHA512(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha512"}


class AttributeSHA512_224(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha512/224"}


class AttributeSHA512_256(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha512/256"}


class AttributeSHA3_224(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha3-224"}


class AttributeSHA3_256(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha3-256"}


class AttributeSHA3_384(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha3-384"}


class AttributeSHA3_512(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "sha3-512"}


class AttributeTLSH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "tlsh"}


class AttributeCDHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "cdhash"}


class AttributeFILENAME_AUTHENTIHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|authentihash"}


class AttributeFILENAME_VHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|vhash"}


class AttributeFILENAME_SSDEEP(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|ssdeep"}


class AttributeFILENAME_IMPHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|imphash"}


class AttributeFILENAME_IMPFUZZY(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|impfuzzy"}


class AttributeFILENAME_PEHASH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|pehash"}


class AttributeFILENAME_SHA224(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha224"}


class AttributeFILENAME_SHA384(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha384"}


class AttributeFILENAME_SHA512(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha512"}


class AttributeFILENAME_SHA512_224(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha512/224"}


class AttributeFILENAME_SHA512_256(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha512/256"}


class AttributeFILENAME_SHA3_224(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha3-224"}


class AttributeFILENAME_SHA3_256(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha3-256"}


class AttributeFILENAME_SHA3_384(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha3-384"}


class AttributeFILENAME_SHA3_512(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|sha3-512"}


class AttributeFILENAME_TLSH(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Artifacts dropped", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "filename|tlsh"}


class AttributeWINDOWS_SCHEDULED_TASK(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "windows-scheduled-task"}


class AttributeWINDOWS_SERVICE_NAME(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "windows-service-name"}


class AttributeWINDOWS_SERVICE_DISPLAYNAME(Attribute):
    default_category = "Artifacts dropped"
    categories = ["Artifacts dropped"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "windows-service-displayname"}


class AttributeWHOIS_REGISTRANT_EMAIL(Attribute):
    default_category = "Attribution"
    categories = ["Payload delivery", "Attribution", "Social network"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "whois-registrant-email"}


class AttributeWHOIS_REGISTRANT_PHONE(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "whois-registrant-phone"}


class AttributeWHOIS_REGISTRANT_NAME(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "whois-registrant-name"}


class AttributeWHOIS_REGISTRANT_ORG(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "whois-registrant-org"}


class AttributeWHOIS_REGISTRAR(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "whois-registrar"}


class AttributeWHOIS_CREATION_DATE(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "whois-creation-date"}


class AttributeX509_FINGERPRINT_SHA1(Attribute):
    default_category = "Network activity"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Network activity",
        "Attribution",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "x509-fingerprint-sha1"}


class AttributeX509_FINGERPRINT_MD5(Attribute):
    default_category = "Network activity"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Network activity",
        "Attribution",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "x509-fingerprint-md5"}


class AttributeX509_FINGERPRINT_SHA256(Attribute):
    default_category = "Network activity"
    categories = [
        "Payload delivery",
        "Artifacts dropped",
        "Payload installation",
        "Network activity",
        "Attribution",
        "External analysis",
    ]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "x509-fingerprint-sha256"}


class AttributeDNS_SOA_EMAIL(Attribute):
    default_category = "Attribution"
    categories = ["Attribution"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "dns-soa-email"}


class AttributeSIZE_IN_BYTES(Attribute):
    default_category = "Other"
    categories = ["Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "size-in-bytes"}


class AttributeCOUNTER(Attribute):
    default_category = "Other"
    categories = ["Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "counter"}


class AttributeDATETIME(Attribute):
    default_category = "Other"
    categories = ["Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "datetime"}


class AttributePORT(Attribute):
    default_category = "Network activity"
    categories = ["Network activity", "Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "port"}


class AttributeIP_DST_PORT(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "ip-dst|port"}


class AttributeIP_SRC_PORT(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "ip-src|port"}


class AttributeHOSTNAME_PORT(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "hostname|port"}


class AttributeMAC_ADDRESS(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "mac-address"}


class AttributeMAC_EUI_64(Attribute):
    default_category = "Network activity"
    categories = ["Payload delivery", "Network activity", "External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "mac-eui-64"}


class AttributeEMAIL_DST_DISPLAY_NAME(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-dst-display-name"}


class AttributeEMAIL_SRC_DISPLAY_NAME(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-src-display-name"}


class AttributeEMAIL_HEADER(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-header"}


class AttributeEMAIL_REPLY_TO(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-reply-to"}


class AttributeEMAIL_X_MAILER(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-x-mailer"}


class AttributeEMAIL_MIME_BOUNDARY(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-mime-boundary"}


class AttributeEMAIL_THREAD_INDEX(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-thread-index"}


class AttributeEMAIL_MESSAGE_ID(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "email-message-id"}


class AttributeGITHUB_USERNAME(Attribute):
    default_category = "Social network"
    categories = ["Social network"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "github-username"}


class AttributeGITHUB_REPOSITORY(Attribute):
    default_category = "Social network"
    categories = ["External analysis", "Social network"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "github-repository"}


class AttributeGITHUB_ORGANISATION(Attribute):
    default_category = "Social network"
    categories = ["Social network"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "github-organisation"}


class AttributeJABBER_ID(Attribute):
    default_category = "Social network"
    categories = ["Social network"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "jabber-id"}


class AttributeTWITTER_ID(Attribute):
    default_category = "Social network"
    categories = ["Social network"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "twitter-id"}


class AttributeDKIM(Attribute):
    default_category = "Network activity"
    categories = ["Network activity"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "dkim"}


class AttributeDKIM_SIGNATURE(Attribute):
    default_category = "Network activity"
    categories = ["Network activity"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "dkim-signature"}


class AttributeFIRST_NAME(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "first-name"}


class AttributeMIDDLE_NAME(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "middle-name"}


class AttributeLAST_NAME(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "last-name"}


class AttributeFULL_NAME(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "full-name"}


class AttributeDATE_OF_BIRTH(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "date-of-birth"}


class AttributePLACE_OF_BIRTH(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "place-of-birth"}


class AttributeGENDER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "gender"}


class AttributePASSPORT_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "passport-number"}


class AttributePASSPORT_COUNTRY(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "passport-country"}


class AttributePASSPORT_EXPIRATION(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "passport-expiration"}


class AttributeREDRESS_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "redress-number"}


class AttributeNATIONALITY(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "nationality"}


class AttributeVISA_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "visa-number"}


class AttributeISSUE_DATE_OF_THE_VISA(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "issue-date-of-the-visa"}


class AttributePRIMARY_RESIDENCE(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "primary-residence"}


class AttributeCOUNTRY_OF_RESIDENCE(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "country-of-residence"}


class AttributeSPECIAL_SERVICE_REQUEST(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "special-service-request"}


class AttributeFREQUENT_FLYER_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "frequent-flyer-number"}


class AttributeTRAVEL_DETAILS(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "travel-details"}


class AttributePAYMENT_DETAILS(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "payment-details"}


class AttributePLACE_PORT_OF_ORIGINAL_EMBARKATION(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "place-port-of-original-embarkation"}


class AttributePLACE_PORT_OF_CLEARANCE(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "place-port-of-clearance"}


class AttributePLACE_PORT_OF_ONWARD_FOREIGN_DESTINATION(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "place-port-of-onward-foreign-destination"}


class AttributePASSENGER_NAME_RECORD_LOCATOR_NUMBER(Attribute):
    default_category = "Person"
    categories = ["Person"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "passenger-name-record-locator-number"}


class AttributeMOBILE_APPLICATION_ID(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "mobile-application-id"}


class AttributeAZURE_APPLICATION_ID(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "azure-application-id"}


class AttributeCHROME_EXTENSION_ID(Attribute):
    default_category = "Payload delivery"
    categories = ["Payload delivery", "Payload installation"]
    to_ids = True
    __mapper_args__ = {"polymorphic_identity": "chrome-extension-id"}


class AttributeCORTEX(Attribute):
    default_category = "External analysis"
    categories = ["External analysis"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "cortex"}


class AttributeBOOLEAN(Attribute):
    default_category = "Other"
    categories = ["Other"]
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "boolean"}


class AttributeANONYMISED(Attribute):
    default_category = "Other"
    categories = [
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
    to_ids = False
    __mapper_args__ = {"polymorphic_identity": "anonymised"}
