from ...environment import client, environment


def test_users_me() -> None:
    response = client.get("/users/view/me", headers={"authorization": environment.site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json.get("User").get("id") == str(environment.site_admin_user.id)
