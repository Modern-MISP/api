from ...environment import client
from ..helpers.noticelists_helper import (
    add_noticelists,
    get_invalid_noticelist_ids,
    get_non_existing_noticelist_ids,
    remove_noticelists,
)


def test_get_existing_noticelist_details(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = add_noticelists()

    for noticelist_id in noticelist_ids:
        response = client.get(f"/noticelists/{noticelist_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["Noticelist"]["id"] == str(noticelist_id)

    remove_noticelists(noticelist_ids)

def test_get_existing_noticelist_details_deprecated(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = add_noticelists()

    for noticelist_id in noticelist_ids:
        response = client.get(f"/noticelists/view/{noticelist_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["Noticelist"]["id"] == str(noticelist_id)

    remove_noticelists(noticelist_ids)

def test_get_invalid_noticelist_details(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    invalid_noticelist_ids = get_invalid_noticelist_ids()

    for invalid_noticelist_id in invalid_noticelist_ids:
        response = client.get(f"/noticelists/{invalid_noticelist_id}", headers=headers)
        assert response.status_code == 422

def test_get_invalid_noticelist_details_deprecated(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    invalid_noticelist_ids = get_invalid_noticelist_ids()

    for invalid_noticelist_id in invalid_noticelist_ids:
        response = client.get(f"/noticelists/view/{invalid_noticelist_id}", headers=headers)
        assert response.status_code == 422

def test_get_non_existing_noticelist_details(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    non_existing_noticelist_ids = get_non_existing_noticelist_ids()

    for non_existing_noticelist_id in non_existing_noticelist_ids:
        response = client.get(f"/noticelists/{non_existing_noticelist_id}", headers=headers)
        assert response.status_code == 404

def test_get_non_existing_noticelist_details_deprecated(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    non_existing_noticelist_ids = get_non_existing_noticelist_ids()

    for non_existing_noticelist_id in non_existing_noticelist_ids:
        response = client.get(f"/noticelists/view/{non_existing_noticelist_id}", headers=headers)
        assert response.status_code == 404

def test_get_noticelist_response_format(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_id = add_noticelists(1)

    response = client.get(f"/noticelists/{noticelist_id[0]}", headers=headers)
    json = response.json()
    assert isinstance(json["Noticelist"]["id"], str)

    remove_noticelists(noticelist_id)

def test_get_noticelist_response_format_deprecated(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_id = add_noticelists(1)

    response = client.get(f"/noticelists/view/{noticelist_id[0]}", headers=headers)
    json = response.json()
    assert isinstance(json["Noticelist"]["id"], str)

    remove_noticelists(noticelist_id)


def test_toggleEnable_noticelist(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = add_noticelists(3)

    for noticelist_id in noticelist_ids:
        response = client.post(f"/noticelists/toggleEnable/{noticelist_id}", headers=headers)

        assert response.status_code == 200
        json = response.json()
        assert json["message"] == "Noticelist disabled."

        response = client.post(f"/noticelists/toggleEnable/{noticelist_id}", headers=headers)

        assert response.status_code == 200
        json = response.json()
        assert json["message"] == "Noticelist enabled."

        response = client.post(f"/noticelists/toggleEnable/{noticelist_id}", headers=headers)

        assert response.status_code == 200
        json = response.json()
        assert json["message"] == "Noticelist disabled."

    remove_noticelists(noticelist_ids)

def test_toggleEnable_invalid_noticelist(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    invalid_noticelist_ids = get_invalid_noticelist_ids()

    for invalid_noticelist_id in invalid_noticelist_ids:
        response = client.post(f"/noticelists/toggleEnable/{invalid_noticelist_id}", headers=headers)
        assert response.status_code == 422

def test_toggleEnable_non_existing_noticelist_details(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    non_existing_noticelist_ids = get_non_existing_noticelist_ids()

    for non_existing_noticelist_id in non_existing_noticelist_ids:
        response = client.post(f"/noticelists/toggleEnable/{non_existing_noticelist_id}", headers=headers)
        assert response.status_code == 404

def test_noticelist_toggleEnable_response_format(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_id = add_noticelists(1)

    response = client.post(f"noticelists/toggleEnable/{noticelist_id[0]}", headers=headers)
    json = response.json()
    assert json["id"] == str(noticelist_id[0])
    assert json["saved"]

    remove_noticelists(noticelist_id)


def test_update_noticelist(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.put("/noticelists", headers=headers)
    assert response.status_code == 200

    response = client.post("/noticelists/update", headers=headers)
    assert response.status_code == 200

def test_update_noticelist_deprecated(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.post("/noticelists/update", headers=headers)
    assert response.status_code == 200

def test_update_noticelist_response_format(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.put("/noticelists", headers=headers)
    json = response.json()
    assert json["url"] == "/noticelists/"

def test_update_noticelist_response_format_deprecated(site_admin_user_token) -> None:
        headers = {"authorization": site_admin_user_token}
        response = client.post("/noticelists/update", headers=headers)
        assert response.headers["Content-Type"] == "application/json"
        json = response.json()
        assert json["url"] == "/noticelists/update"


def test_get_all_noticelist(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.get("/noticelists", headers=headers)

    assert response.status_code == 200

def test_get_noticelist_response_format2(site_admin_user_token) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = add_noticelists()

    response = client.get("/noticelists", headers=headers)
    json = response.json()
    assert isinstance(json, list)

    remove_noticelists(noticelist_ids)
