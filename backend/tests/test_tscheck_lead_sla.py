"""SLA warning levels follow the 24h/48h thresholds and only apply while status is 'new'."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_seeded_critical_lead_flagged_and_fresh_lead_is_ok(client):
    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    leads = client.get("/admin/leads?scope=all")
    assert leads.status_code == 200, leads.text
    critical_candidates = [l for l in leads.json() if l["status"] == "new" and l["age_hours"] >= 48]
    assert critical_candidates, "expected a seeded lead older than 48h with status new"
    seeded_critical = critical_candidates[0]
    assert seeded_critical["sla_level"] == "critical"

    # a brand-new lead (age ~0h) must not carry any SLA warning
    suffix = uuid.uuid4().hex[:8]
    fresh = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-sla-fresh-{suffix}", "phone": f"0812990000{suffix[:2]}", "major": "RPL"},
    )
    assert fresh.status_code == 201, fresh.text
    fresh_lead = fresh.json()
    assert fresh_lead["sla_level"] == "ok"
    assert fresh_lead["age_hours"] == 0

    # once status leaves 'new' the SLA warning must clear, even though age keeps growing
    follow = client.patch(f"/admin/leads/{fresh_lead['id']}", json={"status": "follow_up"})
    assert follow.status_code == 200, follow.text
    assert follow.json()["sla_level"] == "ok"

    refreshed = client.get("/admin/leads?scope=all")
    row = next(r for r in refreshed.json() if r["id"] == fresh_lead["id"])
    assert row["status"] == "follow_up"
    assert row["sla_level"] == "ok"
