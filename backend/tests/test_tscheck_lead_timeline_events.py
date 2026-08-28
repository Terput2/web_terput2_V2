"""Lead timeline merges created/assignment/status/note/whatsapp events, newest-first, without losing existing history."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_timeline_combines_all_event_types_chronologically(client):
    suffix = uuid.uuid4().hex[:8]

    login_admin = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin.status_code == 200, login_admin.text

    officer_email = f"tscheck-tloff-{suffix}@example.com"
    officer_resp = client.post(
        "/admin/users",
        json={"name": f"tscheck-tloff-{suffix}", "email": officer_email, "role": "ppdb_officer", "password": "TscheckPass2026!"},
    )
    assert officer_resp.status_code == 201, officer_resp.text
    officer_id = officer_resp.json()["id"]

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-timeline-{suffix}", "phone": f"0813900000{suffix[:2]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead_id = lead_resp.json()["id"]
    lead_name = lead_resp.json()["name"]

    assign_resp = client.patch(f"/admin/leads/{lead_id}", json={"assigned_to_id": officer_id})
    assert assign_resp.status_code == 200, assign_resp.text

    status_resp = client.patch(f"/admin/leads/{lead_id}", json={"status": "follow_up"})
    assert status_resp.status_code == 200, status_resp.text

    note_resp = client.post(f"/admin/leads/{lead_id}/notes", json={"text": f"tscheck note {suffix}"})
    assert note_resp.status_code == 201, note_resp.text

    wa_resp = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": "greeting"})
    assert wa_resp.status_code == 201, wa_resp.text

    timeline_resp = client.get(f"/admin/leads/{lead_id}/timeline")
    assert timeline_resp.status_code == 200, timeline_resp.text
    events = timeline_resp.json()
    types = [event["event_type"] for event in events]

    assert "created" in types
    assert "assignment" in types
    assert "status" in types
    assert "note" in types
    assert "whatsapp" in types
    assert len(events) >= 5

    # newest-first ordering
    timestamps = [event["created_at"] for event in events]
    assert timestamps == sorted(timestamps, reverse=True)

    note_event = next(event for event in events if event["event_type"] == "note")
    assert f"tscheck note {suffix}" in note_event["description"]
    assert note_event["actor_name"]  # actor recorded (admin display name)

    wa_event = next(event for event in events if event["event_type"] == "whatsapp")
    assert lead_name in wa_event["description"]
    assert wa_event["metadata"].get("template") == "greeting"

    created_event = next(event for event in events if event["event_type"] == "created")
    assert created_event["actor_name"] == "Sistem"

    # cleanup officer fixture
    delete_resp = client.delete(f"/admin/users/{officer_id}")
    assert delete_resp.status_code == 200, delete_resp.text
