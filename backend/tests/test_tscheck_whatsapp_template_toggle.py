"""A template can be deactivated (rejecting WhatsApp actions with 422 while inactive) and the
"Default" reset restores its original content and re-activates it."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"

DEFAULT_DOCUMENTS_CONTENT = (
    "Halo {nama}, kami mengingatkan kelengkapan berkas PPDB {sekolah} untuk jurusan {jurusan}. "
    "Mohon konfirmasi jika berkas sudah siap."
)


def test_template_deactivate_rejects_action_and_reset_restores(client):
    suffix = uuid.uuid4().hex[:8]
    target_key = "documents"

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-toggle-{suffix}", "phone": f"08159300{suffix[:6]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead_id = lead_resp.json()["id"]

    # deactivate the template
    deactivate = client.patch(f"/admin/whatsapp-templates/{target_key}", json={"is_active": False})
    assert deactivate.status_code == 200, deactivate.text
    assert deactivate.json()["is_active"] is False

    # inactive template used gets 422, not silently accepted
    rejected = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": target_key})
    assert rejected.status_code == 422, rejected.text

    # Default button (reset endpoint) restores original content AND reactivates it
    reset_resp = client.post(f"/admin/whatsapp-templates/{target_key}/reset")
    assert reset_resp.status_code == 200, reset_resp.text
    restored = reset_resp.json()
    assert restored["is_active"] is True
    assert restored["content"] == DEFAULT_DOCUMENTS_CONTENT

    # now the same action succeeds again
    accepted = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": target_key})
    assert accepted.status_code == 201, accepted.text
