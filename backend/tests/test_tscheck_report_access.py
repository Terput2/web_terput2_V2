"""Only Super Admin can view or run the weekly report; other roles are rejected."""
PPDB_EMAIL = "ppdb@terataiputih2.sch.id"
PPDB_PASSWORD = "PpdbTeratai2026!"
EDITOR_EMAIL = "editor@terataiputih2.sch.id"
EDITOR_PASSWORD = "EditorTeratai2026!"
AGENDA_EMAIL = "agenda@terataiputih2.sch.id"
AGENDA_PASSWORD = "AgendaTeratai2026!"


def test_non_super_admin_roles_cannot_access_reports(client):
    for email, password in [
        (PPDB_EMAIL, PPDB_PASSWORD),
        (EDITOR_EMAIL, EDITOR_PASSWORD),
        (AGENDA_EMAIL, AGENDA_PASSWORD),
    ]:
        login = client.post("/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text

        overview = client.get("/admin/reports")
        assert overview.status_code == 403, f"{email}: {overview.text}"

        run_resp = client.post("/admin/reports/run")
        assert run_resp.status_code == 403, f"{email}: {run_resp.text}"

        client.post("/auth/logout")
