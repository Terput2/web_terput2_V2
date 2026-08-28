"""Super Admin can run a weekly report simulation; it is stored as 'simulated', appears in history, and is audited."""
ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_report_simulation_persists_and_is_audited(client):
    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    run_resp = client.post("/admin/reports/run")
    assert run_resp.status_code == 201, run_resp.text
    run = run_resp.json()
    assert run["status"] == "simulated"
    assert run["trigger"] == "manual"
    assert run["delivery_mode"] == "simulated"
    assert run["recipient"]

    overview = client.get("/admin/reports")
    assert overview.status_code == 200, overview.text
    body = overview.json()
    assert any(r["id"] == run["id"] for r in body["runs"])
    preview = body["preview"]
    assert set(["total", "overdue", "duplicates", "top_major", "busiest_officer"]).issubset(preview.keys())
    assert body["schedule"] == "Setiap Senin, 07.00 WIB"
    assert body["next_run"]

    audit = client.get("/admin/audit", params={"action": "report_simulated"})
    assert audit.status_code == 200, audit.text
    assert any(a["entity_id"] == run["id"] or a["action"] == "report_simulated" for a in audit.json())
    assert any(a["action"] == "report_simulated" for a in audit.json())
