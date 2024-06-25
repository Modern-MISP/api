def test_users_me(site_admin_user_token, site_admin_user, client) -> None:
    response = client.get("/users/view/me", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json.get("User").get("id") == str(site_admin_user.id)


def test_users_create(site_admin_user_token, client) -> None:
    respone = client.post("/users", headers={"authorization": site_admin_user_token})

    assert respone.status_code == 200
