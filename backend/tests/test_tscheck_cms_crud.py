"""Admin can create, update (title/status), and delete CMS content for each resource."""
import uuid

import pytest

ADMIN_EMAIL = "admin@terataiputih2.sch.id"
ADMIN_PASSWORD = "TerataiAdmin2026!"


@pytest.fixture
def admin_client(client):
    resp = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, resp.text
    return client


@pytest.mark.parametrize("resource", ["news", "agenda", "gallery", "major"])
def test_admin_can_create_update_delete_content(admin_client, resource):
    suffix = uuid.uuid4().hex[:8]
    title = f"tscheck-{resource}-{suffix}"
    create_resp = admin_client.post(
        "/admin/content",
        json={"resource": resource, "title": title, "description": "seed", "is_published": True},
    )
    assert create_resp.status_code == 201, create_resp.text
    item = create_resp.json()
    item_id = item["id"]
    assert item["title"] == title
    assert item["is_published"] is True

    updated_title = f"{title}-updated"
    update_resp = admin_client.patch(
        f"/admin/content/{item_id}", json={"title": updated_title, "is_published": False}
    )
    assert update_resp.status_code == 200, update_resp.text
    updated = update_resp.json()
    assert updated["title"] == updated_title
    assert updated["is_published"] is False

    list_resp = admin_client.get(f"/admin/content/{resource}")
    assert list_resp.status_code == 200, list_resp.text
    assert any(row["id"] == item_id for row in list_resp.json())

    delete_resp = admin_client.delete(f"/admin/content/{item_id}")
    assert delete_resp.status_code == 200, delete_resp.text

    list_after = admin_client.get(f"/admin/content/{resource}")
    assert all(row["id"] != item_id for row in list_after.json())


def test_create_content_without_session_rejected(client):
    resp = client.post(
        "/admin/content",
        json={"resource": "news", "title": "tscheck-unauthorized", "description": "x"},
    )
    assert resp.status_code == 401, resp.text
