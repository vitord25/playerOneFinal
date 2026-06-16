"""
Testes de autenticação — registro e login (RF20 / RF22).
"""
from tests.conftest import register_user, login_user


def test_register_user_success(client):
    """Um novo usuário deve ser criado com sucesso (201) e nascer como USER."""
    resp = register_user(client, name="Bob", email="bob@example.com", password="secret123")
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert data["email"] == "bob@example.com"
    assert data["name"] == "Bob"
    assert data["role"] == "USER"          # novos usuários nunca nascem ADMIN
    assert data["active"] is True
    assert "id" in data
    assert "password" not in data          # senha nunca é exposta


def test_register_duplicate_email_conflict(client):
    """Registrar o mesmo e-mail duas vezes deve retornar 409 (RN04)."""
    register_user(client, email="dup@example.com")
    resp = register_user(client, email="dup@example.com")
    assert resp.status_code == 409, resp.text


def test_register_invalid_email(client):
    """E-mail inválido deve ser rejeitado pela validação do schema (422)."""
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "X", "email": "not-an-email", "password": "secret123"},
    )
    assert resp.status_code == 422


def test_login_success_returns_token(client):
    """Login com credenciais válidas deve retornar um JWT (RF22)."""
    register_user(client, email="login@example.com", password="secret123")
    resp = login_user(client, email="login@example.com", password="secret123")
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert isinstance(data["access_token"], str)


def test_login_wrong_password_unauthorized(client):
    """Senha incorreta deve retornar 401."""
    register_user(client, email="wp@example.com", password="secret123")
    resp = login_user(client, email="wp@example.com", password="wrongpass")
    assert resp.status_code == 401, resp.text


def test_me_endpoint_with_token(client):
    """GET /auth/me deve retornar o usuário autenticado com um token válido."""
    register_user(client, name="Carol", email="carol@example.com", password="secret123")
    token = login_user(client, email="carol@example.com", password="secret123").json()["access_token"]

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["email"] == "carol@example.com"


def test_me_endpoint_without_token_unauthorized(client):
    """GET /auth/me sem token deve retornar 401."""
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
