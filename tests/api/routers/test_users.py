from tests.environment import client, environment


def test_users_me():
    response = client.get("/users/view/me", headers={})  # use authorization=environment.user_token

    assert response.status_code == 200
    json = response.json()
    assert json.get("User").get("id") == environment.user_id

    return
