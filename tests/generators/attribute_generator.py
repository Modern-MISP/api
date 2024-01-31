from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody
from mmisp.api_schemas.attributes.edit_attribute_body import EditAttributeBody


def generate_valid_add_attribute_data() -> AddAttributeBody:
    return AddAttributeBody(
        value="1.2.3.4",
        type="ip-src",
        category="Network activity",
        to_ids=True,
        distribution="1",
        comment="test_comment",
        disable_correlation=False,
    )


def generate_missing_required_field_add_attribute_data() -> AddAttributeBody:
    return AddAttributeBody(value="1.2.3.4")


def generate_invalid_required_field_add_attribute_data() -> AddAttributeBody:
    return AddAttributeBody(value="1.2.3.4", type="invalid type")


def generate_invalid_field_add_attribute_data() -> AddAttributeBody:
    return AddAttributeBody(value="1.2.3.4", type="ip-src", category=1)


def generate_existing_attribute_id() -> str:
    return "1"


def generate_non_existing_attribute_id() -> str:
    return "0"


def generate_invalid_attribute_id() -> str:
    return "invalid id"


def generate_valid_edit_attribute_data() -> EditAttributeBody:
    return EditAttributeBody(
        category="Payload delivery",
        value="2.3.4.5",
        to_ids=True,
        distribution="1",
        comment="new_comment",
        disable_correlation=False,
    )
