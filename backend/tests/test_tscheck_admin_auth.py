"""Admin CMS auth: valid login opens session, invalid rejected, admin route needs session."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_valid_login_opens_session_and_admin_route(client):
    resp = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["email"] == ADMIN_EMAIL
    assert "school_admin_session" in resp.cookies

    me_resp = client.get("/auth/me")
    assert me_resp.status_code == 200, me_resp.text
    assert me_resp.json()["email"] == ADMIN_EMAIL

    admin_resp = client.get("/admin/leads")
    assert admin_resp.status_code == 200, admin_resp.text


def test_invalid_login_rejected(client):
    resp = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": f"wrong-{uuid.uuid4()}"})
    assert resp.status_code == 401, resp.text


def test_admin_route_without_session_returns_401(client):
    resp = client.get("/admin/leads")
    assert resp.status_code == 401, resp.text
    resp2 = client.get("/admin/content/news")
    assert resp2.status_code == 401, resp2.text
