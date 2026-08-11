from fastapi.testclient import TestClient

from tests.test_avatars import register_and_authenticate


def create_avatar(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "Luna", "slug": "luna"},
    )
    assert response.status_code == 201
    return response.json()


def test_avatar_media_crud_and_profile_selection(client: TestClient) -> None:
    headers = register_and_authenticate(client)
    avatar = create_avatar(client, headers)
    media_url = f"/api/v1/avatars/{avatar['id']}/media"

    create_response = client.post(
        media_url,
        headers=headers,
        json={
            "media_type": "image",
            "storage_key": f"avatars/{avatar['id']}/images/profile.webp",
            "thumbnail_key": f"avatars/{avatar['id']}/thumbnails/profile.webp",
            "mime_type": "image/webp",
            "width": 1024,
            "height": 1024,
        },
    )
    assert create_response.status_code == 201
    media = create_response.json()
    assert media["media_type"] == "image"
    assert media["avatar_id"] == avatar["id"]

    list_response = client.get(media_url, headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [media["id"]]

    profile_response = client.patch(
        f"/api/v1/avatars/{avatar['id']}",
        headers=headers,
        json={"profile_media_id": media["id"]},
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["profile_media_id"] == media["id"]

    update_response = client.patch(
        f"{media_url}/{media['id']}",
        headers=headers,
        json={"width": 512, "height": 512},
    )
    assert update_response.status_code == 200
    assert update_response.json()["width"] == 512

    assert client.delete(f"{media_url}/{media['id']}", headers=headers).status_code == 204
    avatar_response = client.get(f"/api/v1/avatars/{avatar['id']}", headers=headers)
    assert avatar_response.json()["profile_media_id"] is None


def test_video_cannot_be_selected_as_profile_media(client: TestClient) -> None:
    headers = register_and_authenticate(client)
    avatar = create_avatar(client, headers)
    media_response = client.post(
        f"/api/v1/avatars/{avatar['id']}/media",
        headers=headers,
        json={
            "media_type": "video",
            "storage_key": f"avatars/{avatar['id']}/videos/intro.mp4",
            "mime_type": "video/mp4",
            "duration_seconds": 8.5,
        },
    )
    media = media_response.json()

    response = client.patch(
        f"/api/v1/avatars/{avatar['id']}",
        headers=headers,
        json={"profile_media_id": media["id"]},
    )
    assert response.status_code == 422


def test_user_cannot_manage_another_avatars_media(client: TestClient) -> None:
    first_headers = register_and_authenticate(client)
    avatar = create_avatar(client, first_headers)
    second_headers = register_and_authenticate(
        client, email="other@example.com", username="other_user"
    )

    response = client.post(
        f"/api/v1/avatars/{avatar['id']}/media",
        headers=second_headers,
        json={"media_type": "image", "storage_key": "not/owned.webp"},
    )
    assert response.status_code == 404
