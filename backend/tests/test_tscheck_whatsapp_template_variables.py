"""WhatsApp template variables {nama}/{jurusan}/{petugas}/{sekolah} are substituted with real
data when a message is generated; an unsupported placeholder is rejected with 422 at edit time."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_variables_are_substituted_and_unsupported_placeholder_rejected(client):
    suffix = uuid.uuid4().hex[:8]
    target_key = "greeting"

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    content = "Halo {nama} dari {sekolah}, jurusan {jurusan} ditangani oleh {petugas}."
    patch_resp = client.patch(f"/admin/whatsapp-templates/{target_key}", json={"content": content})
    assert patch_resp.status_code == 200, patch_resp.text

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-var-{suffix}", "phone": f"08159400{suffix[:6]}", "major": "TKJ"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead = lead_resp.json()

    action_resp = client.post(f"/admin/leads/{lead['id']}/whatsapp", json={"template": target_key})
    assert action_resp.status_code == 201, action_resp.text
    message = action_resp.json()["message"]
    assert lead["name"] in message
    assert "SMK Teratai Putih Global 2 Bekasi" in message
    assert "TKJ" in message
    assert "Super Admin" in message or "admin" in message.lower()
    # no leftover unresolved placeholders
    assert "{nama}" not in message and "{jurusan}" not in message
    assert "{petugas}" not in message and "{sekolah}" not in message

    # unsupported placeholder is rejected, template left untouched
    bad_resp = client.patch(
        f"/admin/whatsapp-templates/{target_key}",
        json={"content": "Halo {nama}, kode promo {kode_promo} berlaku."},
    )
    assert bad_resp.status_code == 422, bad_resp.text

    unchanged = client.get("/admin/whatsapp-templates")
    assert unchanged.status_code == 200, unchanged.text
    current = next(item for item in unchanged.json() if item["key"] == target_key)
    assert current["content"] == content

    # restore default
    reset_resp = client.post(f"/admin/whatsapp-templates/{target_key}/reset")
    assert reset_resp.status_code == 200, reset_resp.text
