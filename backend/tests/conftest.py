"""
Configuração compartilhada de testes (pytest).

Estratégia:
    - Usa um banco SQLite em memória (StaticPool) para isolar os testes,
      evitando a necessidade de um MySQL real.
    - Sobrescreve a dependência `get_db` do FastAPI para usar a sessão de teste.
    - Sobrescreve `publish_event` do RabbitMQ por um no-op assíncrono, para que
      os testes não dependam de um broker rodando.
    - Expõe fixtures de `client` (TestClient) e helpers de autenticação.

Execução:
    cd projeto_final_backend
    pytest -v
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Garante que a raiz do projeto esteja no sys.path (para importar `src...`)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Variáveis de ambiente mínimas para o Settings carregar sem um .env de produção
os.environ.setdefault("MYSQL_HOST", "localhost")
os.environ.setdefault("MYSQL_DATABASE", "test")
os.environ.setdefault("MYSQL_USER", "test")
os.environ.setdefault("MYSQL_PASSWORD", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret")
os.environ.setdefault("RABBITMQ_HOST", "localhost")
os.environ.setdefault("RABBITMQ_USER", "guest")
os.environ.setdefault("RABBITMQ_PASSWORD", "guest")

from src.app.core.database import Base, get_db  # noqa: E402
from src.app import models  # noqa: E402,F401  (registra modelos no metadata)


# -----------------------------------------------------------------------------
# Engine SQLite em memória (compartilhado entre conexões via StaticPool)
# -----------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def _reset_database():
    """Recria todas as tabelas antes de cada teste e descarta ao final."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(monkeypatch):
    """
    TestClient com:
      - get_db sobrescrito para usar SQLite de teste
      - publish_event neutralizado (no-op) para não exigir RabbitMQ
    """
    # Neutraliza a publicação de eventos no RabbitMQ durante os testes
    async def _noop_publish_event(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "src.app.internal.rabbitmq.publish_event", _noop_publish_event
    )
    # Os services importam `publish_event` diretamente; corrige cada módulo
    for module in (
        "src.app.services.party_service",
        "src.app.services.party_member_service",
        "src.app.services.user_service",
    ):
        monkeypatch.setattr(f"{module}.publish_event", _noop_publish_event, raising=False)

    # Importa o app só depois dos patches de ambiente
    from src.main import app

    def _override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db

    # NÃO usamos `with TestClient(app)` para evitar disparar o lifespan
    # (que tentaria conectar ao MySQL/RabbitMQ no startup).
    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()


# -----------------------------------------------------------------------------
# Helpers de autenticação reutilizáveis
# -----------------------------------------------------------------------------
def register_user(client, name="Alice", email="alice@example.com", password="secret123"):
    return client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": password},
    )


def login_user(client, email="alice@example.com", password="secret123"):
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return resp


def auth_header(client, email="alice@example.com", password="secret123"):
    """Registra (se necessário) + faz login e devolve o header Authorization."""
    register_user(client, email=email, password=password, name=email.split("@")[0])
    token = login_user(client, email=email, password=password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
