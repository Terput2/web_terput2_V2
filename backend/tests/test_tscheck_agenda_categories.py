"""Agenda items support the five fixed categories and the public API returns them."""

import uuid

SUPER_ADMIN = {"email": "admin@terataiputih2.sch.id", "password": "TerataiAdmin2026!"}
CATEGORIES = ["akademik", "ujian", "kegiatan", "industri", "pengumuman"]


def login(client):
    resp = client.post("/auth/login", json=SUPER_ADMIN)
    assert resp.status_code == 200, resp.text
    return resp.cookies


def test_all_five_categories_persist_and_appear_publicly(client):
    cookies = login(client)
    suffix = uuid.uuid4().hex[:8]
    created_ids = {}

    for category in CATEGORIES:
        title = f"tscheck-agenda-cat-{category}-{suffix}"
        resp = client.post(
            "/admin/content",
            json={"resource": "agenda", "title": title, "category": category, "is_published": True},
            cookies=cookies,
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["category"] == category
        created_ids[category] = body["id"]

    public_resp = client.get("/content/agenda")
    assert public_resp.status_code == 200, public_resp.text
    public_by_id = {item["id"]: item for item in public_resp.json()}

    for category, item_id in created_ids.items():
        assert item_id in public_by_id, f"{category} agenda item missing from public API"
        assert public_by_id[item_id]["category"] == category

    for item_id in created_ids.values():
        client.delete(f"/admin/content/{item_id}", cookies=cookies)


def test_invalid_category_rejected(client):
    cookies = login(client)
    resp = client.post(
        "/admin/content",
        json={"resource": "agenda", "title": "tscheck-agenda-invalid-category", "category": "invalid_cat"},
        cookies=cookies,
    )
    assert resp.status_code == 422, resp.text
