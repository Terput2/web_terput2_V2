"""Two leads sharing the same WhatsApp number are both kept and cross-linked as duplicates."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_repeated_phone_number_marks_both_leads_duplicate(client):
    suffix = uuid.uuid4().hex[:10]
    phone = "081" + str(int(suffix, 16))[-9:]
    name_a = f"tscheck-dup-a-{suffix}"
    name_b = f"tscheck-dup-b-{suffix}"

    first = client.post("/leads", json={"kind": "ppdb", "name": name_a, "phone": phone, "major": "TKJ"})
    assert first.status_code == 201, first.text
    lead_a = first.json()
    baseline_duplicate_ids = list(lead_a["duplicate_ids"])

    second = client.post("/leads", json={"kind": "contact", "name": name_b, "phone": phone, "question": "tscheck dup"})
    assert second.status_code == 201, second.text
    lead_b = second.json()
    assert lead_b["duplicate_ids"] == [lead_a["id"]]
    assert lead_a["normalized_phone"] == lead_b["normalized_phone"]

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    # lead_a should now be updated (via $addToSet) to reference lead_b as duplicate,
    # and duplicate_count is computed dynamically on the admin listing
    admin_leads = client.get("/admin/leads?scope=all")
    assert admin_leads.status_code == 200, admin_leads.text
    row_a = next(r for r in admin_leads.json() if r["id"] == lead_a["id"])
    row_b = next(r for r in admin_leads.json() if r["id"] == lead_b["id"])
    assert lead_b["id"] in row_a["duplicate_ids"]
    assert set(row_a["duplicate_ids"]) == set(baseline_duplicate_ids) | {lead_b["id"]}
    assert row_a["duplicate_count"] == len(baseline_duplicate_ids) + 1
    assert row_b["duplicate_count"] == 1

    # duplicates endpoint returns full history for both linked leads, ordered oldest first
    history = client.get(f"/admin/leads/{lead_b['id']}/duplicates")
    assert history.status_code == 200, history.text
    history_ids = [item["id"] for item in history.json()]
    assert lead_a["id"] in history_ids and lead_b["id"] in history_ids
