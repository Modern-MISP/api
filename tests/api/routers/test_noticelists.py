import pytest

from ..helpers.noticelists_helper import (
    add_noticelists,
    get_invalid_noticelist_ids,
    get_non_existing_noticelist_ids,
    remove_noticelists,
)


@pytest.mark.asyncio
async def test_get_existing_noticelist_details(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = await add_noticelists(db)

    for noticelist_id in noticelist_ids:
        response = client.get(f"/noticelists/{noticelist_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["Noticelist"]["id"] == noticelist_id

    await remove_noticelists(db, noticelist_ids)


@pytest.mark.asyncio
async def test_get_existing_noticelist_details_deprecated(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = await add_noticelists(db)

    for noticelist_id in noticelist_ids:
        response = client.get(f"/noticelists/view/{noticelist_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["Noticelist"]["id"] == noticelist_id

    await remove_noticelists(db, noticelist_ids)


@pytest.mark.asyncio
async def test_get_invalid_noticelist_details(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    invalid_noticelist_ids = get_invalid_noticelist_ids()

    for invalid_noticelist_id in invalid_noticelist_ids:
        response = client.get(f"/noticelists/{invalid_noticelist_id}", headers=headers)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_invalid_noticelist_details_deprecated(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    invalid_noticelist_ids = get_invalid_noticelist_ids()

    for invalid_noticelist_id in invalid_noticelist_ids:
        response = client.get(f"/noticelists/view/{invalid_noticelist_id}", headers=headers)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_non_existing_noticelist_details(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    non_existing_noticelist_ids = await get_non_existing_noticelist_ids(db)

    for non_existing_noticelist_id in non_existing_noticelist_ids:
        response = client.get(f"/noticelists/{non_existing_noticelist_id}", headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_non_existing_noticelist_details_deprecated(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    non_existing_noticelist_ids = await get_non_existing_noticelist_ids(db)

    for non_existing_noticelist_id in non_existing_noticelist_ids:
        response = client.get(f"/noticelists/view/{non_existing_noticelist_id}", headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_noticelist_response_format(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_id = await add_noticelists(db, 1)

    response = client.get(f"/noticelists/{noticelist_id[0]}", headers=headers)
    json = response.json()
    assert isinstance(json["Noticelist"]["id"], int)

    await remove_noticelists(db, noticelist_id)


@pytest.mark.asyncio
async def test_get_noticelist_response_format_deprecated(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_id = await add_noticelists(db, 1)

    response = client.get(f"/noticelists/view/{noticelist_id[0]}", headers=headers)
    json = response.json()
    assert isinstance(json["Noticelist"]["id"], int)

    await remove_noticelists(db, noticelist_id)


@pytest.mark.asyncio
async def test_toggleEnable_noticelist(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = await add_noticelists(db, 3)

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

    await remove_noticelists(db, noticelist_ids)


@pytest.mark.asyncio
async def test_toggleEnable_invalid_noticelist(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    invalid_noticelist_ids = get_invalid_noticelist_ids()

    for invalid_noticelist_id in invalid_noticelist_ids:
        response = client.post(f"/noticelists/toggleEnable/{invalid_noticelist_id}", headers=headers)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_toggleEnable_non_existing_noticelist_details(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    non_existing_noticelist_ids = await get_non_existing_noticelist_ids(db)

    for non_existing_noticelist_id in non_existing_noticelist_ids:
        response = client.post(f"/noticelists/toggleEnable/{non_existing_noticelist_id}", headers=headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_noticelist_toggleEnable_response_format(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_id = await add_noticelists(db, 1)

    response = client.post(f"noticelists/toggleEnable/{noticelist_id[0]}", headers=headers)
    json = response.json()
    assert json["id"] == noticelist_id[0]
    assert json["saved"]

    await remove_noticelists(db, noticelist_id)


@pytest.mark.asyncio
async def test_update_noticelist(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.put("/noticelists", headers=headers)
    assert response.status_code == 200

    response = client.post("/noticelists/update", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_noticelist_deprecated(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.post("/noticelists/update", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_noticelist_response_format(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.put("/noticelists", headers=headers)
    json = response.json()
    assert json["url"] == "/noticelists/"


@pytest.mark.asyncio
async def test_update_noticelist_response_format_deprecated(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/noticelists/update", headers=headers)
    assert response.headers["Content-Type"] == "application/json"
    json = response.json()
    assert json["url"] == "/noticelists/update"


@pytest.mark.asyncio
async def test_get_all_noticelist(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    response = client.get("/noticelists", headers=headers)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_noticelist_response_format2(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}

    noticelist_ids = await add_noticelists(db)

    response = client.get("/noticelists", headers=headers)
    json = response.json()
    assert isinstance(json, list)

    await remove_noticelists(db, noticelist_ids)
