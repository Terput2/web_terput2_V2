"""Role-based access for WhatsApp template management: Super Admin can edit/reset; Super
Admin and PPDB officer can read active templates; content editor and agenda manager cannot
read or edit templates."""
ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"
PPDB_EMAIL = "ppdb@terataiputih2.sch.id"
PPDB_PASSWORD = "PpdbTeratai2026!"
EDITOR_EMAIL = "editor@terataiputih2.sch.id"
EDITOR_PASSWORD = "EditorTeratai2026!"
AGENDA_EMAIL = "agenda@terataiputih2.sch.id"
AGENDA_PASSWORD = "AgendaTeratai2026!"


def test_template_rbac_by_role(client):
    # PPDB officer can read templates but cannot edit/reset them
    login_ppdb = client.post("/auth/login", json={"email": PPDB_EMAIL, "password": PPDB_PASSWORD})
    assert login_ppdb.status_code == 200, login_ppdb.text
    ppdb_read = client.get("/admin/whatsapp-templates")
    assert ppdb_read.status_code == 200, ppdb_read.text
    assert len(ppdb_read.json()) >= 4
    ppdb_edit = client.patch("/admin/whatsapp-templates/greeting", json={"content": "Halo {nama}, tidak sah."})
    assert ppdb_edit.status_code == 403, ppdb_edit.text
    ppdb_reset = client.post("/admin/whatsapp-templates/greeting/reset")
    assert ppdb_reset.status_code == 403, ppdb_reset.text

    # content editor has no leads/template access at all
    login_editor = client.post("/auth/login", json={"email": EDITOR_EMAIL, "password": EDITOR_PASSWORD})
    assert login_editor.status_code == 200, login_editor.text
    editor_read = client.get("/admin/whatsapp-templates")
    assert editor_read.status_code == 403, editor_read.text
    editor_edit = client.patch("/admin/whatsapp-templates/greeting", json={"content": "Halo {nama}, tidak sah."})
    assert editor_edit.status_code == 403, editor_edit.text

    # agenda manager likewise has no access
    login_agenda = client.post("/auth/login", json={"email": AGENDA_EMAIL, "password": AGENDA_PASSWORD})
    assert login_agenda.status_code == 200, login_agenda.text
    agenda_read = client.get("/admin/whatsapp-templates")
    assert agenda_read.status_code == 403, agenda_read.text
    agenda_edit = client.patch("/admin/whatsapp-templates/greeting", json={"content": "Halo {nama}, tidak sah."})
    assert agenda_edit.status_code == 403, agenda_edit.text

    # super admin can both read and edit/reset
    login_admin = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin.status_code == 200, login_admin.text
    admin_read = client.get("/admin/whatsapp-templates")
    assert admin_read.status_code == 200, admin_read.text
    admin_edit = client.patch("/admin/whatsapp-templates/greeting", json={"is_active": True})
    assert admin_edit.status_code == 200, admin_edit.text
    admin_reset = client.post("/admin/whatsapp-templates/greeting/reset")
    assert admin_reset.status_code == 200, admin_reset.text
