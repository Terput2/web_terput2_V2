"""PPDB Officer role only manages leads (with filters) and is denied content/users management."""

PPDB = {"email": "ppdb@terataiputih2.sch.id", "password": "PpdbTeratai2026!"}


def login(client):
    resp = client.post("/auth/login", json=PPDB)
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "ppdb_officer"
    return resp.cookies


def test_ppdb_officer_can_view_and_filter_leads(client):
    cookies = login(client)
    resp = client.get("/admin/leads", cookies=cookies)
    assert resp.status_code == 200, resp.text

    filtered = client.get("/admin/leads", params={"kind": "ppdb", "status": "new"}, cookies=cookies)
    assert filtered.status_code == 200, filtered.text
    for lead in filtered.json():
        assert lead["kind"] == "ppdb"
        assert lead["status"] == "new"

    date_filtered = client.get(
        "/admin/leads", params={"start_date": "2020-01-01", "end_date": "2020-01-02"}, cookies=cookies
    )
    assert date_filtered.status_code == 200, date_filtered.text


def test_ppdb_officer_denied_content_and_users(client):
    cookies = login(client)

    for resource in ("news", "agenda", "gallery", "major"):
        resp = client.get(f"/admin/content/{resource}", cookies=cookies)
        assert resp.status_code == 403, f"{resource}: {resp.text}"

    create_resp = client.post(
        "/admin/content", json={"resource": "news", "title": "TSCheck News Blocked"}, cookies=cookies
    )
    assert create_resp.status_code == 403, create_resp.text

    users_resp = client.get("/admin/users", cookies=cookies)
    assert users_resp.status_code == 403, users_resp.text
