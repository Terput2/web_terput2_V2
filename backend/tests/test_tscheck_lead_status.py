"""Admin can move a lead through status transitions and it persists (survives a fresh read)."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_lead_status_transitions_persist(client):
    suffix = uuid.uuid4().hex[:8]
    name = f"tscheck-status-{suffix}"
    phone = f"0812{int(suffix, 16) % 100000000:08d}"
    create_resp = client.post(
        "/leads",
        json={"kind": "contact", "name": name, "phone": phone, "question": "tscheck"},
    )
    assert create_resp.status_code == 201, create_resp.text
    lead_id = create_resp.json()["id"]

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    follow_resp = client.patch(f"/admin/leads/{lead_id}", json={"status": "follow_up"})
    assert follow_resp.status_code == 200, follow_resp.text
    assert follow_resp.json()["status"] == "follow_up"

    # simulate refresh: fresh GET of admin leads list reflects the persisted status
    refreshed = client.get("/admin/leads")
    assert refreshed.status_code == 200, refreshed.text
    row = next(r for r in refreshed.json() if r["id"] == lead_id)
    assert row["status"] == "follow_up"

    done_resp = client.patch(f"/admin/leads/{lead_id}", json={"status": "done"})
    assert done_resp.status_code == 200, done_resp.text
    assert done_resp.json()["status"] == "done"

    refreshed_again = client.get("/admin/leads")
    row2 = next(r for r in refreshed_again.json() if r["id"] == lead_id)
    assert row2["status"] == "done"
