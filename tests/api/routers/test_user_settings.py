from time import time
from typing import Any

from mmisp.db.models.user_setting import SettingName, UserSetting
from tests.database import get_db
from tests.environment import client, environment
from tests.generators.model_generators.user_setting_generator import generate_user_setting


class TestSetUserSetting:
    @staticmethod
    def test_set_user_setting() -> None:
        db = get_db()
        body = {"value": {"attribute": str(time())}}

        user_id = environment.site_admin_user.id
        setting = SettingName.DEFAULT_RESTSEARCH_PARAMETERS.value

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post(
            f"/user_settings/setSetting/{user_id}/{setting}",
            json=body,
            headers=headers,
        )

        cleanup_setting = (
            db.query(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == setting).first()
        )

        db.delete(cleanup_setting)
        db.commit()

        assert response.status_code == 200
        json = response.json()

        assert json["UserSetting"]["value"] == body["value"]

    @staticmethod
    def test_set_user_setting_override_existing() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()

        body: dict[str, Any] = {"value": {}}

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.post(
            f"/user_settings/setSetting/{user_setting.user_id}/{user_setting.setting}",
            json=body,
            headers=headers,
        )

        assert response.status_code == 200
        json = response.json()

        db.delete(user_setting)
        db.commit()

        assert not json["UserSetting"]["value"].get("attribute", None)

    @staticmethod
    def test_set_user_setting_no_perms() -> None:
        body: dict[str, Any] = {"value": {}}

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.post(
            f"/user_settings/setSetting/{environment.instance_two_owner_org_admin_user.id}/{SettingName.EVENT_INDEX_HIDE_COLUMNS.value}",
            json=body,
            headers=headers,
        )

        assert response.status_code == 404

    body: dict[str, Any] = {"value": {}}


class TestGetUserSetting:
    @staticmethod
    def test_get_existing_user_setting_details() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/user_settings/{user_setting.id}", headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 200
        json = response.json()

        assert json["UserSetting"]["id"] == str(user_setting.id)
        assert isinstance(json["UserSetting"], dict)

    @staticmethod
    def test_get_non_existing_user_setting_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/user_settings/-1", headers=headers)

        assert response.status_code == 404

    @staticmethod
    def test_get_user_setting_without_perms() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.instance_two_owner_org_admin_user_token}
        response = client.get(f"/user_settings/{user_setting.id}", headers=headers)

        db.delete(user_setting)
        db.commit()
        assert response.status_code == 404


class TestGetUseSettingByUserIdAndSettingName:
    @staticmethod
    def test_get_existing_user_setting_details() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.get(f"/user_settings/{user_setting.user_id}/{user_setting.setting}", headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 200
        json = response.json()

        assert json["UserSetting"]["user_id"] == str(environment.instance_owner_org_admin_user.id)
        assert json["UserSetting"]["setting"] == user_setting.setting

    @staticmethod
    def test_get_user_setting_by_invalid_us_name_uid() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.get(f"/user_settings/{user_setting.user_id}/invalid", headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 404

    @staticmethod
    def test_get_non_existing_user_setting_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get(f"/user_settings/-1/{SettingName.TAG_NUMERICAL_VALUE_OVERRIDE.value}", headers=headers)

        assert response.status_code == 404

    @staticmethod
    def test_get_user_setting_without_perms() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()

        headers = {"authorization": environment.instance_two_owner_org_admin_user_token}
        response = client.get(f"/user_settings/{user_setting.user_id}/{user_setting.setting}", headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 404


class TestSearchUserSetting:
    @staticmethod
    def test_search_existing_user_setting_details() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/user_settings", headers=headers, json={})

        assert response.status_code == 200

    @staticmethod
    def test_search_non_existing_user_setting_details() -> None:
        body = {"setting": "doesnt exist"}

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.post("/user_settings", headers=headers, json=body)

        assert response.status_code == 200
        json = response.json()

        assert len(json) == 0

    @staticmethod
    def test_search_user_setting_using_ids() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        body = {"id": str(user_setting.id), "user_id": str(user_setting.user_id)}

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.post("/user_settings", json=body, headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 200
        json = response.json()

        assert json[0]["UserSetting"]["id"] == str(user_setting.id)


class TestGetAllUserSettings:
    @staticmethod
    def test_get_all_user_settings() -> None:
        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/user_settings", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert isinstance(json, list)

    @staticmethod
    def test_get_all_user_settings_using_site_admin() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_two_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.site_admin_user_token}
        response = client.get("/user_settings", headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 200
        json = response.json()

        assert next((setting for setting in json if setting["UserSetting"]["id"] == str(user_setting.id)), None)


class TestDeleteUserSetting:
    @staticmethod
    def test_delete_user_setting() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.delete(f"/user_settings/{user_setting.id}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["saved"]
        assert json["success"]
        assert "delete" not in json["url"]
        assert json["id"] == str(user_setting.id)

    @staticmethod
    def test_delete_user_setting_depr() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.delete(f"/user_settings/delete/{user_setting.id}", headers=headers)

        assert response.status_code == 200
        json = response.json()

        assert json["saved"]
        assert json["success"]
        assert "delete" in json["url"]
        assert json["id"] == str(user_setting.id)

    @staticmethod
    def test_delete_user_setting_lesser_perms() -> None:
        db = get_db()

        user_setting = generate_user_setting()
        user_setting.user_id = environment.instance_two_owner_org_admin_user.id

        db.add(user_setting)
        db.commit()
        db.refresh(user_setting)

        headers = {"authorization": environment.instance_owner_org_admin_user_token}
        response = client.delete(f"/user_settings/{user_setting.id}", headers=headers)

        db.delete(user_setting)
        db.commit()

        assert response.status_code == 404
