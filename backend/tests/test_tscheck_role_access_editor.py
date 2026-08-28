"""Content Editor role is restricted to news/gallery/major content; leads/agenda/users are 403."""

EDITOR = {"email": "editor@terataiputih2.sch.id", "password": "EditorTeratai2026!"}


def login(client):
    resp = client.post("/auth/login", json=EDITOR)
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "content_editor"
    return resp.cookies


def test_editor_can_access_allowed_content(client):
    cookies = login(client)
    for resource in ("news", "gallery", "major"):
        resp = client.get(f"/admin/content/{resource}", cookies=cookies)
        assert resp.status_code == 200, f"{resource}: {resp.text}"


def test_editor_denied_agenda_leads_and_users(client):
    cookies = login(client)

    agenda_resp = client.get("/admin/content/agenda", cookies=cookies)
    assert agenda_resp.status_code == 403, agenda_resp.text

    leads_resp = client.get("/admin/leads", cookies=cookies)
    assert leads_resp.status_code == 403, leads_resp.text

    users_resp = client.get("/admin/users", cookies=cookies)
    assert users_resp.status_code == 403, users_resp.text

    create_agenda = client.post(
        "/admin/content",
        json={"resource": "agenda", "title": "TSCheck Agenda Blocked"},
        cookies=cookies,
    )
    assert create_agenda.status_code == 403, create_agenda.text
