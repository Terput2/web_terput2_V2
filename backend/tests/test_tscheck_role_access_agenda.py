"""Agenda Manager role only manages agenda content; other resources/leads/users are 403."""

AGENDA_MANAGER = {"email": "agenda@terataiputih2.sch.id", "password": "AgendaTeratai2026!"}


def login(client):
    resp = client.post("/auth/login", json=AGENDA_MANAGER)
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "agenda_manager"
    return resp.cookies


def test_agenda_manager_can_manage_agenda(client):
    cookies = login(client)
    resp = client.get("/admin/content/agenda", cookies=cookies)
    assert resp.status_code == 200, resp.text

    create_resp = client.post(
        "/admin/content",
        json={"resource": "agenda", "title": "tscheck-agenda-role-item", "category": "kegiatan"},
        cookies=cookies,
    )
    assert create_resp.status_code == 201, create_resp.text
    item_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/admin/content/{item_id}", cookies=cookies)
    assert delete_resp.status_code == 200, delete_resp.text


def test_agenda_manager_denied_other_resources_leads_and_users(client):
    cookies = login(client)

    for resource in ("news", "gallery", "major"):
        resp = client.get(f"/admin/content/{resource}", cookies=cookies)
        assert resp.status_code == 403, f"{resource}: {resp.text}"

    leads_resp = client.get("/admin/leads", cookies=cookies)
    assert leads_resp.status_code == 403, leads_resp.text

    users_resp = client.get("/admin/users", cookies=cookies)
    assert users_resp.status_code == 403, users_resp.text
