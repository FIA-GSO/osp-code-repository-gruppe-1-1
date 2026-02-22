def test_index_requires_login(client):
    res = client.get("/")
    assert res.status_code == 302
    assert "/login" in res.headers.get("Location", "")


def test_index_logged_in(logged_in_client):
    res = logged_in_client.get("/")
    assert res.status_code == 200


def test_search_query_logged_in(logged_in_client):
    res = logged_in_client.get("/?q=flask")
    assert res.status_code == 200