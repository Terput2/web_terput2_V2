"""RBAC for lead timeline & WhatsApp actions: super admin and assigned PPDB officer can use them,
an unrelated PPDB officer and non-lead roles (editor, agenda) are rejected."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"
PPDB_EMAIL = "ppdb@terataiputih2.sch.id"
PPDB_PASSWORD = "PpdbTeratai2026!"
EDITOR_EMAIL = "editor@terataiputih2.sch.id"
EDITOR_PASSWORD = "EditorTeratai2026!"
AGENDA_EMAIL = "agenda@terataiputih2.sch.id"
AGENDA_PASSWORD = "AgendaTeratai2026!"


def test_timeline_and_whatsapp_rbac(client):
    suffix = uuid.uuid4().hex[:8]

    login_admin = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin.status_code == 200, login_admin.text

    officer_email = f"tscheck-rbacoff-{suffix}@example.com"
    officer_resp = client.post(
        "/admin/users",
        json={"name": f"tscheck-rbacoff-{suffix}", "email": officer_email, "role": "ppdb_officer", "password": "TscheckPass2026!"},
    )
    assert officer_resp.status_code == 201, officer_resp.text
    officer_id = officer_resp.json()["id"]

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-rbac-{suffix}", "phone": f"08159200{suffix[:6]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead_id = lead_resp.json()["id"]

    assign_resp = client.patch(f"/admin/leads/{lead_id}", json={"assigned_to_id": officer_id})
    assert assign_resp.status_code == 200, assign_resp.text

    # unrelated PPDB officer (default seeded one) is denied timeline + whatsapp on this lead
    login_ppdb = client.post("/auth/login", json={"email": PPDB_EMAIL, "password": PPDB_PASSWORD})
    assert login_ppdb.status_code == 200, login_ppdb.text
    denied_timeline = client.get(f"/admin/leads/{lead_id}/timeline")
    assert denied_timeline.status_code == 403, denied_timeline.text
    denied_wa = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": "greeting"})
    assert denied_wa.status_code == 403, denied_wa.text

    # content editor and agenda manager have no leads access at all
    login_editor = client.post("/auth/login", json={"email": EDITOR_EMAIL, "password": EDITOR_PASSWORD})
    assert login_editor.status_code == 200, login_editor.text
    editor_timeline = client.get(f"/admin/leads/{lead_id}/timeline")
    assert editor_timeline.status_code == 403, editor_timeline.text
    editor_wa = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": "greeting"})
    assert editor_wa.status_code == 403, editor_wa.text

    login_agenda = client.post("/auth/login", json={"email": AGENDA_EMAIL, "password": AGENDA_PASSWORD})
    assert login_agenda.status_code == 200, login_agenda.text
    agenda_timeline = client.get(f"/admin/leads/{lead_id}/timeline")
    assert agenda_timeline.status_code == 403, agenda_timeline.text
    agenda_wa = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": "greeting"})
    assert agenda_wa.status_code == 403, agenda_wa.text

    # super admin succeeds
    login_admin2 = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin2.status_code == 200, login_admin2.text
    admin_timeline = client.get(f"/admin/leads/{lead_id}/timeline")
    assert admin_timeline.status_code == 200, admin_timeline.text
    admin_wa = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": "greeting"})
    assert admin_wa.status_code == 201, admin_wa.text

    # cleanup: officer fixture account
    delete_resp = client.delete(f"/admin/users/{officer_id}")
    assert delete_resp.status_code == 200, delete_resp.text
