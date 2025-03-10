import pytest
import pytest_asyncio
import sqlalchemy as sa
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from mmisp.lib.permissions import Permission

from mmisp.db.models.attribute import AttributeTag
from mmisp.tests.generators.model_generators.tag_generator import generate_tag


@pytest.mark.asyncio
async def test_get_existing_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get(f"/attributes/{attribute_id}", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_existing_attribute_fail_read_only_user(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.get(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_attributes(
    access_test_objects,
    client,
) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get("/attributes", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    assert len(response_json) == 1


@pytest.mark.asyncio
async def test_get_all_attributes_read_only_user(
    access_test_objects,
    client,
) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.get("/attributes", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_existing_attribute(access_test_objects, client) -> None:
    attribute_id = access_test_objects["default_attribute"].id

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.delete(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_existing_attribute_fail_read_only_user(access_test_objects, client) -> None:
    attribute_id = access_test_objects["default_attribute"].id

    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    response = client.delete(f"/attributes/{attribute_id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_attribute_fail_read_only_user(access_test_objects, client) -> None:
    request_body = {
        "value": "1.2.3.4",
        "type": "ip-src",
        "category": "Network activity",
        "to_ids": True,
        "distribution": "1",
        "comment": "test comment",
        "disable_correlation": False,
    }
    event_id = access_test_objects["default_event"].id

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.post(f"/attributes/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_existing_tag_to_attribute(
    access_test_objects,
    client,
) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/addTag/{attribute_id}/{tag_id}/local:1", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute(
    access_test_objects,
    access_test_user_token,
    client,
) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_fail(
    access_test_objects,
    client,
) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    attribute_id = access_test_objects["attribute_no_access"].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)
    assert response.status_code == 200
    print(response.json())


@pytest.mark.asyncio
async def test_remove_existing_tag_from_attribute_fail_read_only_user(
    access_test_objects,
    client,
) -> None:
    headers = {"authorization": access_test_objects["default_read_only_user_token"]}
    attribute_id = access_test_objects["default_attribute"].id
    tag_id = access_test_objects["default_tag"].id
    response = client.post(f"/attributes/removeTag/{attribute_id}/{tag_id}", headers=headers)
    assert response.status_code == 200
    print(response.json())


@pytest.mark.asyncio
async def test_restore_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_Id = access_test_objects["default_attribute"].id
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.post(f"/attributes/restore/{attribute_Id}", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["Attribute"]["id"] == attribute_Id
    assert response_json["Attribute"]["deleted"] is False


@pytest.mark.asyncio
async def test_remove_tag_from_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_Id = access_test_objects["default_attribute"].id
    tag_Id = access_test_objects["default_tag"].id
    headers = {"authorization": access_test_objects["default_user_token"]}
    response2 = client.post(f"/attributes/addTag/{attribute_Id}/{tag_Id}", headers=headers)
    response = client.post(f"/attributes/removeTag/{attribute_Id}/{tag_Id}", headers=headers)
    # Der status code liefert immer 200 zurück egal, ob klappt oder wie in diesem Fall fehlschlägt.
    assert response.status_code == 200
    response_json = response.json()
    response2_json = response2.json()
    print(response2_json)
    print(response_json)


@pytest.mark.asyncio
async def test_update_attribute(
    access_test_objects,
    client,
) -> None:
    attribute_id = access_test_objects["default_attribute"].id
    request_body = {
        "category": "Payload delivery",
        "value": "2.3.4.5",
        "to_ids": True,
        "distribution": "1",
        "comment": "new comment",
        "disable_correlation": False,
        "first_seen": "",
    }
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.put(f"/attributes/{attribute_id}", json=request_body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    assert response_json["Attribute"]["id"] == attribute_id
    assert response_json["Attribute"]["category"] == "Payload delivery"


@pytest.mark.asyncio
async def test_get_all_attributes_site_admin(
    access_test_objects,
    client,
) -> None:
    headers = {"authorization": access_test_objects["site_admin_user_token"]}
    response = client.get("/attributes", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    print(response_json)
    assert isinstance(response_json, list)
    assert len(response_json) == 4


@pytest.mark.asyncio
async def test_delete_selected_attributes_from_existing_event(access_test_objects, client) -> None:
    request_body = {"id": "1 2", "allow_hard_delete": False}
    event_id = access_test_objects["default_event"].id

    attribute_id = access_test_objects["default_attribute"].id
    attribute2_id = access_test_objects["default_attribute_2"].id

    attribute_ids = str(attribute_id) + " " + str(attribute2_id)

    request_body["id"] = attribute_ids

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.post(f"/attributes/deleteSelected/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_selected_attributes_from_existing_event_fail(access_test_objects, client) -> None:
    request_body = {"id": "1 2", "allow_hard_delete": False}
    event_id = access_test_objects["default_event"].id

    attribute_id = access_test_objects["attribute_no_access"].id
    attribute2_id = access_test_objects["attribute_no_access_2"].id

    attribute_ids = str(attribute_id) + " " + str(attribute2_id)

    request_body["id"] = attribute_ids

    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.post(f"/attributes/deleteSelected/{event_id}", json=request_body, headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_attribute_type_absolute_statistics(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get("/attributes/attributeStatistics/type/0", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_attribute_type_relative_statistics(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get("/attributes/attributeStatistics/type/1", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_attribute_category_absolute_statistics(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get("/attributes/attributeStatistics/category/0", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_attribute_category_relative_statistics(access_test_objects, client) -> None:
    headers = {"authorization": access_test_objects["default_user_token"]}
    response = client.get("/attributes/attributeStatistics/category/1", headers=headers)
    assert response.status_code == 200
