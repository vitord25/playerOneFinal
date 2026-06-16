"""
Testes de Parties — criação e listagem (RF08 / RF10 / RF11).

Para criar uma party é necessário um Jogo disponível. Como os endpoints de
criação de jogo exigem ADMIN, os testes inserem o jogo diretamente no banco
de teste (via sessão SQLite) para focar no fluxo de parties.
"""
from tests.conftest import TestingSessionLocal, register_user, login_user


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _seed_game(name="Catan", quantity=2, available=True):
    """Insere um jogo diretamente no banco de teste e devolve seu id."""
    from src.app.models.game import Game

    session = TestingSessionLocal()
    try:
        game = Game(
            name=name,
            description="Jogo de estratégia",
            minimum_age=10,
            category="Estratégia",
            quantity=quantity,
            available=available,
            min_players=3,
            max_players=4,
            min_duration_minutes=60,
            max_duration_minutes=120,
        )
        session.add(game)
        session.commit()
        session.refresh(game)
        return game.id
    finally:
        session.close()


def _token(client, email="org@example.com", password="secret123"):
    register_user(client, name="Organizador", email=email, password=password)
    return login_user(client, email=email, password=password).json()["access_token"]


def _party_payload(game_id, max_players=4):
    return {
        "game_id": game_id,
        "description": "Party de teste",
        "date": "2030-01-01",
        "time": "19:00:00",
        "location": "Sala 1",
        "max_players": max_players,
    }


# -----------------------------------------------------------------------------
# Testes
# -----------------------------------------------------------------------------
def test_create_party_success(client):
    """Usuário autenticado cria uma party com jogo disponível (RF08)."""
    game_id = _seed_game()
    token = _token(client)

    resp = client.post(
        "/api/v1/parties/",
        json=_party_payload(game_id),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert data["game_id"] == game_id
    assert data["status"] == "PENDING"      # RN18 - nasce PENDING
    assert data["max_players"] == 4
    assert "id" in data


def test_create_party_requires_auth(client):
    """Criar party sem token deve retornar 401."""
    game_id = _seed_game()
    resp = client.post("/api/v1/parties/", json=_party_payload(game_id))
    assert resp.status_code == 401


def test_create_party_nonexistent_game(client):
    """Criar party com jogo inexistente deve retornar 404 (RN11)."""
    token = _token(client)
    resp = client.post(
        "/api/v1/parties/",
        json=_party_payload(9999),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404, resp.text


def test_list_my_parties(client):
    """GET /parties/my lista as parties do organizador autenticado (RF11)."""
    game_id = _seed_game()
    token = _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/api/v1/parties/", json=_party_payload(game_id), headers=headers)
    assert create.status_code == 201, create.text

    resp = client.get("/api/v1/parties/my", headers=headers)
    assert resp.status_code == 200, resp.text

    parties = resp.json()
    assert isinstance(parties, list)
    assert len(parties) == 1
    assert parties[0]["game_id"] == game_id


def test_list_open_parties_empty(client):
    """GET /parties/open retorna lista vazia quando não há parties aprovadas."""
    token = _token(client)
    resp = client.get(
        "/api/v1/parties/open",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


def test_list_all_parties_requires_admin(client):
    """GET /parties/ exige ADMIN — usuário comum recebe 403."""
    token = _token(client)
    resp = client.get(
        "/api/v1/parties/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403, resp.text
