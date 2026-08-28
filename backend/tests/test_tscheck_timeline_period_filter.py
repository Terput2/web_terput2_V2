"""Lead timeline period filter (7/30/90 days, and a custom start/end date range) filters
events by created_at without disturbing newest-first ordering; an invalid `days` value is
rejected with 422."""
import uuid
from datetime import datetime, timedelta, timezone

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_timeline_period_filter(client):
    suffix = uuid.uuid4().hex[:8]

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-period-{suffix}", "phone": f"08159600{suffix[:6]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead_id = lead_resp.json()["id"]

    note_resp = client.post(f"/admin/leads/{lead_id}/notes", json={"text": f"catatan periode {suffix}"})
    assert note_resp.status_code == 201, note_resp.text

    # a fresh lead's events fall within the last 7/30/90 day windows
    for days in (7, 30, 90):
        resp = client.get(f"/admin/leads/{lead_id}/timeline", params={"days": days})
        assert resp.status_code == 200, resp.text
        events = resp.json()
        assert len(events) >= 2  # created + note
        timestamps = [event["created_at"] for event in events]
        assert timestamps == sorted(timestamps, reverse=True)

    # invalid period value rejected
    invalid_resp = client.get(f"/admin/leads/{lead_id}/timeline", params={"days": 15})
    assert invalid_resp.status_code == 422, invalid_resp.text

    # custom date range covering today includes the events
    today = datetime.now(timezone.utc).date()
    start_date = (today - timedelta(days=1)).isoformat()
    end_date = (today + timedelta(days=1)).isoformat()
    custom_resp = client.get(
        f"/admin/leads/{lead_id}/timeline",
        params={"start_date": start_date, "end_date": end_date},
    )
    assert custom_resp.status_code == 200, custom_resp.text
    custom_events = custom_resp.json()
    assert len(custom_events) >= 2

    # custom date range in the far past excludes the events entirely
    far_past_start = (today - timedelta(days=400)).isoformat()
    far_past_end = (today - timedelta(days=390)).isoformat()
    excluded_resp = client.get(
        f"/admin/leads/{lead_id}/timeline",
        params={"start_date": far_past_start, "end_date": far_past_end},
    )
    assert excluded_resp.status_code == 200, excluded_resp.text
    assert excluded_resp.json() == []
