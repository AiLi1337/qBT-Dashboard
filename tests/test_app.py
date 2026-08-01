from __future__ import annotations


def test_login_required_for_pages_and_api(client):
    page_response = client.get("/", follow_redirects=False)
    assert page_response.status_code == 303
    assert page_response.headers["location"] == "/login"

    api_response = client.get("/api/v1/instances")
    assert api_response.status_code == 401


def test_login_and_create_instance(client):
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    assert login_response.status_code == 303
    csrf_cookie = client.cookies.get("qbpanel_csrf")

    response = client.post(
        "/api/v1/instances",
        headers={"X-CSRF-Token": csrf_cookie},
        json={
            "name": "qb-1",
            "base_url": "http://127.0.0.1:8080",
            "username": "admin",
            "password": "secret",
            "verify_tls": True,
            "enabled": True,
            "reannounce_enabled": True,
            "interval_minutes": 60,
            "request_timeout_seconds": 15,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "qb-1"
    assert data["base_url"] == "http://127.0.0.1:8080"


def test_logout_clears_session(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    csrf_cookie = client.cookies.get("qbpanel_csrf")
    response = client.post("/auth/logout", headers={"X-CSRF-Token": csrf_cookie}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_new_instance_defaults_verify_tls_false(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    csrf_cookie = client.cookies.get("qbpanel_csrf")
    response = client.post(
        "/api/v1/instances",
        headers={"X-CSRF-Token": csrf_cookie},
        json={
            "name": "qb-default-tls",
            "base_url": "http://127.0.0.1:18080",
            "username": "admin",
            "password": "secret",
            "enabled": True,
            "reannounce_enabled": True,
            "interval_minutes": 60,
            "request_timeout_seconds": 15,
        },
    )
    assert response.status_code == 201
    assert response.json()["verify_tls"] is False


def test_edit_and_add_torrent_pages_render(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    csrf_cookie = client.cookies.get("qbpanel_csrf")
    created = client.post(
        "/api/v1/instances",
        headers={"X-CSRF-Token": csrf_cookie},
        json={
            "name": "qb-pages",
            "base_url": "http://127.0.0.1:18081",
            "username": "admin",
            "password": "secret",
            "verify_tls": False,
            "enabled": True,
            "reannounce_enabled": True,
            "interval_minutes": 60,
            "request_timeout_seconds": 15,
        },
    )
    assert created.status_code == 201
    instance_id = created.json()["id"]
    for path in (f"/instances/{instance_id}/edit", f"/instances/{instance_id}/torrents/add"):
        response = client.get(path)
        assert response.status_code == 200
        assert f"data-update-instance-form=\"{instance_id}\"" in response.text or f"data-instance=\"{instance_id}\"" in response.text
