"""PPDB and contact leads persist to MongoDB and show up in admin dashboard."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_ppdb_lead_saved_and_visible_to_admin(client):
    suffix = uuid.uuid4().hex[:8]
    name = f"tscheck-ppdb-{suffix}"
    resp = client.post(
        "/leads",
        json={"kind": "ppdb", "name": name, "phone": "081234567890", "major": "RPL"},
    )
    assert resp.status_code == 201, resp.text
    lead = resp.json()
    assert lead["name"] == name
    assert lead["kind"] == "ppdb"
    assert lead["status"] == "new"

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    admin_leads = client.get("/admin/leads")
    assert admin_leads.status_code == 200, admin_leads.text
    assert any(row["id"] == lead["id"] and row["name"] == name for row in admin_leads.json())


def test_contact_lead_saved_and_visible_to_admin(client):
    suffix = uuid.uuid4().hex[:8]
    name = f"tscheck-contact-{suffix}"
    resp = client.post(
        "/leads",
        json={"kind": "contact", "name": name, "phone": "081234500000", "question": "Berapa biaya SPP?"},
    )
    assert resp.status_code == 201, resp.text
    lead = resp.json()
    assert lead["question"] == "Berapa biaya SPP?"

    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    admin_leads = client.get("/admin/leads")
    assert admin_leads.status_code == 200, admin_leads.text
    assert any(row["id"] == lead["id"] for row in admin_leads.json())
