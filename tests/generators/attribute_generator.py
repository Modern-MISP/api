from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody
from mmisp.api_schemas.attributes.delete_selected_attribute_body import DeleteSelectedAttributeBody
from mmisp.api_schemas.attributes.edit_attribute_body import EditAttributeBody
from mmisp.api_schemas.attributes.search_attributes_body import SearchAttributesBody


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


def generate_existing_id() -> str:
    return "1"


def generate_non_existing_id() -> str:
    return "0"


def generate_invalid_id() -> str:
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


def generate_valid_delete_selected_attributes_data() -> DeleteSelectedAttributeBody:
    return DeleteSelectedAttributeBody(id="1 2 3", allow_hard_delete=False)


def generate_valid_search_attributes_data() -> SearchAttributesBody:
    return SearchAttributesBody(returnFormat="json")


def generate_invalid_search_attributes_data() -> SearchAttributesBody:
    return SearchAttributesBody(returnFormat="invalid format")


def generate_missing_required_field_search_attribute_data() -> SearchAttributesBody:
    return SearchAttributesBody(limit=5)
