"""Super Admin can edit one of the four fixed WhatsApp templates; the change persists
(as seen on a fresh GET, simulating a page refresh), updated_by/updated_at are stamped,
and the change is audited. The template is restored to its default afterwards."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"

EXPECTED_KEYS = {"greeting", "documents", "visit", "final_follow_up"}


def test_super_admin_edits_template_and_it_persists(client):
    suffix = uuid.uuid4().hex[:8]

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    list_resp = client.get("/admin/whatsapp-templates")
    assert list_resp.status_code == 200, list_resp.text
    templates = list_resp.json()
    keys = {item["key"] for item in templates}
    assert EXPECTED_KEYS.issubset(keys), keys

    target_key = "visit"
    new_content = f"Halo {{nama}}, ini pesan tscheck-{suffix} untuk jadwal kunjungan ke {{sekolah}}."

    patch_resp = client.patch(
        f"/admin/whatsapp-templates/{target_key}",
        json={"content": new_content, "is_active": True},
    )
    assert patch_resp.status_code == 200, patch_resp.text
    body = patch_resp.json()
    assert body["content"] == new_content
    assert body["updated_by"]
    assert body["updated_at"]

    # simulate refresh: fresh GET reflects the persisted change
    refreshed = client.get("/admin/whatsapp-templates")
    assert refreshed.status_code == 200, refreshed.text
    refreshed_item = next(item for item in refreshed.json() if item["key"] == target_key)
    assert refreshed_item["content"] == new_content
    assert refreshed_item["updated_by"] == body["updated_by"]

    # audit recorded
    audit_resp = client.get("/admin/audit", params={"action": "whatsapp_template_updated"})
    assert audit_resp.status_code == 200, audit_resp.text
    matching = [entry for entry in audit_resp.json() if entry.get("entity_id") == target_key]
    assert len(matching) >= 1
    assert matching[0]["actor_name"]

    # restore default so the seeded template is not left mutated
    reset_resp = client.post(f"/admin/whatsapp-templates/{target_key}/reset")
    assert reset_resp.status_code == 200, reset_resp.text
    assert new_content not in reset_resp.json()["content"]
