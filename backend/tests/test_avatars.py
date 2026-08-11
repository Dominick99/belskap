from fastapi.testclient import TestClient


def register_and_authenticate(
    client: TestClient,
    email: str = "user@example.com",
    username: str = "test_user",
) -> dict[str, str]:
    password = "a secure password"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_avatar_crud(client: TestClient) -> None:
    headers = register_and_authenticate(client)
    create_response = client.post(
        "/api/v1/avatars",
        headers=headers,
        json={
            "name": "Luna Vale",
            "slug": "luna-vale",
            "bio": "A virtual fashion creator.",
            "visibility": "public",
        },
    )

    assert create_response.status_code == 201
    avatar = create_response.json()
    assert avatar["name"] == "Luna Vale"
    assert avatar["slug"] == "luna-vale"
    assert avatar["visibility"] == "public"
    assert "status" not in avatar

    list_response = client.get("/api/v1/avatars", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [avatar["id"]]

    update_response = client.patch(
        f"/api/v1/avatars/{avatar['id']}",
        headers=headers,
        json={"bio": "An updated biography.", "visibility": "unlisted"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["bio"] == "An updated biography."
    assert update_response.json()["visibility"] == "unlisted"

    delete_response = client.delete(
        f"/api/v1/avatars/{avatar['id']}", headers=headers
    )
    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/avatars/{avatar['id']}", headers=headers).status_code == 404


def test_avatar_routes_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/avatars").status_code == 401
    assert client.post(
        "/api/v1/avatars", json={"name": "Luna", "slug": "luna"}
    ).status_code == 401


def test_slug_is_unique_per_user(client: TestClient) -> None:
    first_headers = register_and_authenticate(client)
    payload = {"name": "Luna", "slug": "luna"}
    assert client.post("/api/v1/avatars", headers=first_headers, json=payload).status_code == 201
    assert client.post("/api/v1/avatars", headers=first_headers, json=payload).status_code == 409

    second_headers = register_and_authenticate(
        client, email="other@example.com", username="other_user"
    )
    assert client.post("/api/v1/avatars", headers=second_headers, json=payload).status_code == 201


def test_user_cannot_access_another_users_avatar(client: TestClient) -> None:
    first_headers = register_and_authenticate(client)
    avatar = client.post(
        "/api/v1/avatars",
        headers=first_headers,
        json={"name": "Luna", "slug": "luna"},
    ).json()
    second_headers = register_and_authenticate(
        client, email="other@example.com", username="other_user"
    )

    assert client.get(
        f"/api/v1/avatars/{avatar['id']}", headers=second_headers
    ).status_code == 404


def test_rejects_invalid_slug_and_visibility(client: TestClient) -> None:
    headers = register_and_authenticate(client)
    assert client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "Luna", "slug": "Not a slug!"},
    ).status_code == 422
    assert client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "Luna", "slug": "luna", "visibility": "friends"},
    ).status_code == 422
    assert client.post(
        "/api/v1/avatars",
        headers=headers,
        json={"name": "   ", "slug": "luna"},
    ).status_code == 422
