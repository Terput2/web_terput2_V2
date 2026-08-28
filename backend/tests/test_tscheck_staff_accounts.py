"""Super Admin can manage multiple staff accounts (create/update/delete)."""

import uuid

SUPER_ADMIN = {"email": "admin@terataiputih2.sch.id", "password": "TerataiAdmin2026!"}


def login(client, creds):
    resp = client.post("/auth/login", json=creds)
    assert resp.status_code == 200, resp.text
    return resp.cookies


def test_super_admin_can_crud_staff_account(client):
    cookies = login(client, SUPER_ADMIN)
    suffix = uuid.uuid4().hex[:8]
    email = f"tscheck-staff-{suffix}@example.com"

    create_resp = client.post(
        "/admin/users",
        json={"email": email, "name": "TSCheck Staff", "password": "TscheckPass2026!", "role": "content_editor"},
        cookies=cookies,
    )
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    admin_id = created["id"]
    assert created["role"] == "content_editor"
    assert created["is_active"] is True

    list_resp = client.get("/admin/users", cookies=cookies)
    assert list_resp.status_code == 200
    assert any(u["id"] == admin_id for u in list_resp.json())

    update_resp = client.patch(
        f"/admin/users/{admin_id}",
        json={"role": "agenda_manager", "is_active": False, "password": "NewTscheckPass2026!"},
        cookies=cookies,
    )
    assert update_resp.status_code == 200, update_resp.text
    updated = update_resp.json()
    assert updated["role"] == "agenda_manager"
    assert updated["is_active"] is False

    # new password works, disabled account still logs in per app rules but role now agenda_manager
    login_resp = client.post("/auth/login", json={"email": email, "password": "NewTscheckPass2026!"})
    assert login_resp.status_code == 200

    delete_resp = client.delete(f"/admin/users/{admin_id}", cookies=cookies)
    assert delete_resp.status_code == 200, delete_resp.text

    list_after = client.get("/admin/users", cookies=cookies)
    assert not any(u["id"] == admin_id for u in list_after.json())


def test_super_admin_cannot_delete_self_and_others_cannot_manage_users(client):
    cookies = login(client, SUPER_ADMIN)
    me = client.get("/auth/me", cookies=cookies).json()

    self_delete = client.delete(f"/admin/users/{me['id']}", cookies=cookies)
    assert self_delete.status_code == 400

    # login as content_editor and confirm no access to user management
    editor_cookies = login(client, {"email": "editor@terataiputih2.sch.id", "password": "EditorTeratai2026!"})
    forbidden = client.get("/admin/users", cookies=editor_cookies)
    assert forbidden.status_code == 403
