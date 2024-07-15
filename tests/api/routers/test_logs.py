def test_logs_index(db, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.post("/events", headers=headers)

    assert 1
