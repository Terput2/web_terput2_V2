"""Each of the four WhatsApp templates produces a personalised, ready-to-send wa.me link and is auditable."""
import uuid
from urllib.parse import unquote

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"

TEMPLATES = ["greeting", "documents", "visit", "final_follow_up"]


def test_whatsapp_templates_generate_personalized_ready_links(client):
    suffix = uuid.uuid4().hex[:8]

    login_admin = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login_admin.status_code == 200, login_admin.text

    lead_resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": f"tscheck-wa-{suffix}", "phone": f"08159100{suffix[:6]}", "major": "RPL"},
    )
    assert lead_resp.status_code == 201, lead_resp.text
    lead = lead_resp.json()
    lead_id = lead["id"]
    lead_name = lead["name"]

    messages = set()
    for template in TEMPLATES:
        resp = client.post(f"/admin/leads/{lead_id}/whatsapp", json={"template": template})
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["template"] == template
        assert lead_name in body["message"]
        messages.add(body["message"])

        assert body["url"].startswith("https://wa.me/62")
        # message text embedded in URL query, url-decodes back to the same message
        query_text = body["url"].split("?text=", 1)[1]
        assert unquote(query_text) == body["message"]

    # each template must produce a distinct message (four genuinely different templates)
    assert len(messages) == len(TEMPLATES)

    # audit trail records each open with actor
    audit_resp = client.get("/admin/audit", params={"action": "whatsapp_opened"})
    assert audit_resp.status_code == 200, audit_resp.text
    entries = [entry for entry in audit_resp.json() if entry.get("entity_id") == lead_id]
    assert len(entries) == len(TEMPLATES)
    for entry in entries:
        assert entry["actor_name"]
        assert entry["details"]["template"] in TEMPLATES
