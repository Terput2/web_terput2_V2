"""Lead timeline supports combining multiple event-type filters (created, assignment, status,
note, whatsapp) via the `types` query param, returning only the selected kinds."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_timeline_multi_type_filter_combination(client):
    suffix = uuid.uuid4().hex[:8]

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-multi-{suffix}", "phone": f"08159500{suffix[:6]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead_id = lead_resp.json()["id"]

    # generate one event of each type: assignment, status, note, whatsapp (created exists already)
    status_resp = client.patch(f"/admin/leads/{lead_id}", json={"status": "follow_up"})
    assert status_resp.status_code == 200, status_resp.text

    note_resp = client.post(f"/admin/leads/{lead_id}/notes", json={"text": f"catatan tscheck {suffix}"})
    assert note_resp.status_code == 201, note_resp.text

    wa_resp = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": "greeting"})
    assert wa_resp.status_code == 201, wa_resp.text

    full_timeline = client.get(f"/admin/leads/{lead_id}/timeline")
    assert full_timeline.status_code == 200, full_timeline.text
    all_types = {event["event_type"] for event in full_timeline.json()}
    assert {"created", "status", "note", "whatsapp"}.issubset(all_types)

    # combination filter: only note + whatsapp
    combo_resp = client.get(f"/admin/leads/{lead_id}/timeline", params={"types": "note,whatsapp"})
    assert combo_resp.status_code == 200, combo_resp.text
    combo_events = combo_resp.json()
    combo_types = {event["event_type"] for event in combo_events}
    assert combo_types == {"note", "whatsapp"}
    assert len(combo_events) == 2

    # combination filter: only created + status
    combo2_resp = client.get(f"/admin/leads/{lead_id}/timeline", params={"types": "created,status"})
    assert combo2_resp.status_code == 200, combo2_resp.text
    combo2_types = {event["event_type"] for event in combo2_resp.json()}
    assert combo2_types == {"created", "status"}

    # newest-first ordering preserved within the filtered set
    timestamps = [event["created_at"] for event in combo_resp.json()]
    assert timestamps == sorted(timestamps, reverse=True)
