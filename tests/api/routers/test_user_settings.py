from time import time
from typing import Any

import pytest
from sqlalchemy import select

from mmisp.db.models.user_setting import SettingName, UserSetting
from mmisp.tests.generators.model_generators.user_setting_generator import generate_user_setting


@pytest.mark.asyncio
async def test_set_user_setting(db, site_admin_user, site_admin_user_token, client) -> None:
    body = {"value": {"attribute": str(time())}}

    user_id = site_admin_user.id
    setting = SettingName.DEFAULT_RESTSEARCH_PARAMETERS.value

    headers = {"authorization": site_admin_user_token}
    response = client.post(
        f"/user_settings/setSetting/me/{setting}",
        json=body,
        headers=headers,
    )

    cleanup_setting = (
        (await db.execute(select(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == setting)))
        .scalars()
        .first()
    )

    await db.delete(cleanup_setting)
    await db.commit()

    assert response.status_code == 200
    json = response.json()

    assert json["UserSetting"]["value"] == body["value"]


@pytest.mark.asyncio
async def test_set_user_setting_override_existing(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()

    body: dict[str, Any] = {"value": {}}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.post(
        f"/user_settings/setSetting/me/{user_setting.setting}",
        json=body,
        headers=headers,
    )

    assert response.status_code == 200
    json = response.json()

    await db.delete(user_setting)
    await db.commit()

    assert not json["UserSetting"]["value"].get("attribute", None)


@pytest.mark.asyncio
async def test_set_user_setting_no_perms(
    instance_owner_org_admin_user_token, instance_two_owner_org_admin_user, client
) -> None:
    body: dict[str, Any] = {"value": {}}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.post(
        f"/user_settings/setSetting/{instance_two_owner_org_admin_user.id}/{SettingName.EVENT_INDEX_HIDE_COLUMNS.value}",
        json=body,
        headers=headers,
    )

    assert response.status_code == 404


body: dict[str, Any] = {"value": {}}


@pytest.mark.asyncio
async def test_get_existing_user_setting_details2(
    db, instance_owner_org_admin_user, site_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/user_settings/{user_setting.id}", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 200
    json = response.json()

    assert json["UserSetting"]["id"] == user_setting.id
    assert isinstance(json["UserSetting"], dict)


@pytest.mark.asyncio
async def test_get_non_existing_user_setting_details2(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/user_settings/-1", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_setting_without_perms(
    db, instance_owner_org_admin_user, instance_org_two_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": instance_org_two_admin_user_token}
    response = client.get(f"/user_settings/{user_setting.id}", headers=headers)

    await db.delete(user_setting)
    await db.commit()
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_existing_user_setting_details(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.get(f"/user_settings/me/{user_setting.setting}", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 200
    json = response.json()

    assert json["UserSetting"]["user_id"] == instance_owner_org_admin_user.id
    assert json["UserSetting"]["setting"] == user_setting.setting


@pytest.mark.asyncio
async def test_get_user_setting_by_invalid_us_name_uid(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.get("/user_settings/me/invalid", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_non_existing_user_setting_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/user_settings/-1/{SettingName.TAG_NUMERICAL_VALUE_OVERRIDE.value}", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_setting_without_perms2(
    db, instance_owner_org_admin_user, instance_org_two_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()

    headers = {"authorization": instance_org_two_admin_user_token}
    response = client.get(f"/user_settings/me/{user_setting.setting}", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_existing_user_setting_details(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/user_settings", headers=headers, json={})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_non_existing_user_setting_details(instance_owner_org_admin_user_token, client) -> None:
    body = {"setting": "doesnt exist"}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.post("/user_settings", headers=headers, json=body)

    assert response.status_code == 200
    json = response.json()

    assert len(json) == 0


@pytest.mark.asyncio
async def test_search_user_setting_using_ids(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    body = {"id": user_setting.id, "user_id": user_setting.user_id}

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.post("/user_settings", json=body, headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 200
    json = response.json()

    assert json[0]["UserSetting"]["id"] == user_setting.id


@pytest.mark.asyncio
async def test_get_all_user_settings(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/user_settings", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert isinstance(json, list)


@pytest.mark.asyncio
async def test_get_all_user_settings_using_site_admin(
    db, instance_two_owner_org_admin_user, site_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_two_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": site_admin_user_token}
    response = client.get("/user_settings", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 200
    json = response.json()

    assert next((setting for setting in json if setting["UserSetting"]["id"] == user_setting.id), None)


@pytest.mark.asyncio
async def test_delete_user_setting(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.delete(f"/user_settings/{user_setting.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["saved"]
    assert json["success"]
    assert "delete" not in json["url"]
    assert json["id"] == user_setting.id


@pytest.mark.asyncio
async def test_delete_user_setting_depr(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.delete(f"/user_settings/delete/{user_setting.id}", headers=headers)

    assert response.status_code == 200
    json = response.json()

    assert json["saved"]
    assert json["success"]
    assert "delete" in json["url"]
    assert json["id"] == user_setting.id


@pytest.mark.asyncio
async def test_delete_user_setting_lesser_perms(
    db, instance_two_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_two_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.delete(f"/user_settings/{user_setting.id}", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_setting_depr(
    db, instance_owner_org_admin_user, instance_owner_org_admin_user_token, client
) -> None:
    user_setting = generate_user_setting()
    user_setting.user_id = instance_owner_org_admin_user.id

    db.add(user_setting)
    await db.commit()
    await db.refresh(user_setting)

    headers = {"authorization": instance_owner_org_admin_user_token}
    response = client.get(f"/user_settings/view/{user_setting.id}", headers=headers)

    await db.delete(user_setting)
    await db.commit()

    assert response.status_code == 200
    json = response.json()

    assert json["UserSetting"]["id"] == user_setting.id
    assert isinstance(json["UserSetting"], dict)
