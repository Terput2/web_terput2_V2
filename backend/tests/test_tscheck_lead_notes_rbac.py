"""Lead-note access stays scoped: officers can't touch another officer's assigned lead, and non-lead roles are rejected outright."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"
PPDB_EMAIL = "ppdb@terataiputih2.sch.id"
PPDB_PASSWORD = "PpdbTeratai2026!"
EDITOR_EMAIL = "editor@terataiputih2.sch.id"
EDITOR_PASSWORD = "EditorTeratai2026!"
AGENDA_EMAIL = "agenda@terataiputih2.sch.id"
AGENDA_PASSWORD = "AgendaTeratai2026!"


def test_note_access_scoped_to_assigned_officer_and_denied_for_other_roles(client):
    suffix = uuid.uuid4().hex[:8]

    login_admin = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin.status_code == 200, login_admin.text

    # create a second PPDB officer account owned by this test
    new_officer_email = f"tscheck-officer-{suffix}@example.com"
    officer_resp = client.post(
        "/admin/users",
        json={"name": f"tscheck-officer-{suffix}", "email": new_officer_email, "role": "ppdb_officer", "password": "TscheckPass2026!"},
    )
    assert officer_resp.status_code == 201, officer_resp.text
    new_officer_id = officer_resp.json()["id"]

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-notesec-{suffix}", "phone": f"0813800000{suffix[:2]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead_id = lead_resp.json()["id"]

    assign_resp = client.patch(f"/admin/leads/{lead_id}", json={"assigned_to_id": new_officer_id})
    assert assign_resp.status_code == 200, assign_resp.text

    # the original (unrelated) PPDB officer must be denied
    login_ppdb = client.post("/auth/login", json={"email": PPDB_EMAIL, "password": PPDB_PASSWORD})
    assert login_ppdb.status_code == 200, login_ppdb.text
    denied_note = client.post(f"/admin/leads/{lead_id}/notes", json={"text": "tscheck should be denied"})
    assert denied_note.status_code == 403, denied_note.text
    denied_list = client.get(f"/admin/leads/{lead_id}/notes")
    assert denied_list.status_code == 200  # listing is allowed for any lead-permission role
    assert denied_list.json() == []

    # content editor and agenda manager have no leads access at all
    login_editor = client.post("/auth/login", json={"email": EDITOR_EMAIL, "password": EDITOR_PASSWORD})
    assert login_editor.status_code == 200, login_editor.text
    editor_note = client.post(f"/admin/leads/{lead_id}/notes", json={"text": "tscheck editor denied"})
    assert editor_note.status_code == 403, editor_note.text
    editor_list = client.get(f"/admin/leads/{lead_id}/notes")
    assert editor_list.status_code == 403, editor_list.text

    login_agenda = client.post("/auth/login", json={"email": AGENDA_EMAIL, "password": AGENDA_PASSWORD})
    assert login_agenda.status_code == 200, login_agenda.text
    agenda_note = client.post(f"/admin/leads/{lead_id}/notes", json={"text": "tscheck agenda denied"})
    assert agenda_note.status_code == 403, agenda_note.text

    # super admin (full access) and the assigned officer succeed
    login_admin2 = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin2.status_code == 200, login_admin2.text
    admin_note = client.post(f"/admin/leads/{lead_id}/notes", json={"text": "tscheck admin allowed"})
    assert admin_note.status_code == 201, admin_note.text

    # cleanup the officer account this test created
    delete_resp = client.delete(f"/admin/users/{new_officer_id}")
    assert delete_resp.status_code == 200, delete_resp.text
