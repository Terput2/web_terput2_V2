"""Public content endpoint only returns is_published=true items; unpublished stays hidden."""
import uuid

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


def test_public_content_hides_unpublished_items(client):
    login = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert login.status_code == 200, login.text

    suffix = uuid.uuid4().hex[:8]
    published_title = f"tscheck-public-visible-{suffix}"
    hidden_title = f"tscheck-public-hidden-{suffix}"

    pub_resp = client.post(
        "/admin/content",
        json={"resource": "gallery", "title": published_title, "description": "x", "is_published": True},
    )
    assert pub_resp.status_code == 201, pub_resp.text
    pub_id = pub_resp.json()["id"]

    hidden_resp = client.post(
        "/admin/content",
        json={"resource": "gallery", "title": hidden_title, "description": "x", "is_published": False},
    )
    assert hidden_resp.status_code == 201, hidden_resp.text
    hidden_id = hidden_resp.json()["id"]

    public_resp = client.get("/content/gallery")
    assert public_resp.status_code == 200, public_resp.text
    public_items = public_resp.json()
    public_ids = {row["id"] for row in public_items}
    assert pub_id in public_ids
    assert hidden_id not in public_ids
    assert all(row["is_published"] for row in public_items)

    client.delete(f"/admin/content/{pub_id}")
    client.delete(f"/admin/content/{hidden_id}")
