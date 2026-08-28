"""Super Admin / PPDB officer can add a follow-up note with author name, timestamp and next action date, persisting across a fresh read."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"
PPDB_EMAIL = "ppdb@terataiputih2.sch.id"
PPDB_PASSWORD = "PpdbTeratai2026!"


def test_officer_can_add_and_reread_followup_note(client):
    suffix = uuid.uuid4().hex[:8]
    create = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-note-{suffix}", "phone": f"0813700000{suffix[:2]}", "major": "TKJ"},
    )
    assert create.status_code == 201, create.text
    lead_id = create.json()["id"]

    login = client.post("/auth/login", json={"email": PPDB_EMAIL, "password": PPDB_PASSWORD})
    assert login.status_code == 200, login.text

    note_resp = client.post(
        f"/admin/leads/{lead_id}/notes",
        json={"text": "tscheck: orang tua sudah dihubungi", "next_action_date": "2026-03-02"},
    )
    assert note_resp.status_code == 201, note_resp.text
    note = note_resp.json()
    assert note["author_name"] == "Petugas PPDB"
    assert note["next_action_date"] == "2026-03-02"
    assert note["created_at"]

    # simulate refresh with a fresh client/session reading the notes list
    login2 = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login2.status_code == 200, login2.text
    listed = client.get(f"/admin/leads/{lead_id}/notes")
    assert listed.status_code == 200, listed.text
    row = next(n for n in listed.json() if n["id"] == note["id"])
    assert row["text"] == "tscheck: orang tua sudah dihubungi"
    assert row["author_name"] == "Petugas PPDB"
