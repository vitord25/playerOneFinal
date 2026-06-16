# 🎲 Ludoteca — Backend (Player One)

API REST para gerenciamento de uma **ludoteca universitária**. O sistema permite o
cadastro de usuários, jogos, criação e moderação de *parties* (sessões de jogo),
gestão de membros das parties, troca de mensagens e auditoria de ações.

O projeto foi construído com **arquitetura em camadas** (Controllers → Services →
Repositories → Models), aplicação de **Design Patterns**, **AOP (Aspect-Oriented
Programming)**, **segurança JWT** com controle de papéis, **mensageria assíncrona**
via RabbitMQ e **observabilidade** com Prometheus + Grafana.

---

## 🧰 Tecnologias Utilizadas

| Categoria | Tecnologia |
|-----------|------------|
| Linguagem | Python 3.11 |
| Framework Web | FastAPI |
| Servidor ASGI | Uvicorn |
| ORM | SQLAlchemy |
| Banco de Dados | MySQL 8.0 |
| Driver MySQL | PyMySQL |
| Validação / Schemas | Pydantic v2 + pydantic-settings |
| Autenticação | JWT (python-jose) + OAuth2 Password Flow |
| Hash de Senha | passlib + bcrypt |
| Mensageria | RabbitMQ (aio-pika) |
| Métricas | Prometheus + prometheus-fastapi-instrumentator |
| Dashboards | Grafana |
| Testes | pytest + httpx (TestClient) |
| Containerização | Docker + Docker Compose |

---

## 🚀 Instruções de Setup e Execução

### Pré-requisitos
- Docker e Docker Compose instalados

### 1. Subir todo o stack com Docker Compose

A partir da pasta `infra/`:

```bash
cd infra
docker-compose up -d --build
```

Isso sobe **todos os serviços**: API, MySQL, RabbitMQ, Prometheus e Grafana.
O schema do banco é aplicado automaticamente a partir de `docs/database/schema.sql`.

Para acompanhar os logs da API:

```bash
docker-compose logs -f api
```

Para derrubar tudo:

```bash
docker-compose down          # mantém os volumes
docker-compose down -v       # remove também os volumes (dados)
```

### 2. Rodar localmente (sem Docker, opcional)

```bash
# A partir da raiz do projeto
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
cp .env.example .env          # ajuste os hosts para "localhost"
uvicorn src.main:app --reload
```

### 3. Rodar os testes

Os testes usam um banco **SQLite em memória** e fazem *mock* do RabbitMQ — não é
necessário ter infraestrutura rodando.

```bash
# A partir da raiz do projeto
pip install -r src/requirements.txt
pytest
```

---

## 🌐 URLs dos Serviços

| Serviço | URL | Observação |
|---------|-----|------------|
| API (raiz) | http://localhost:8000/ | Status da API |
| Health check | http://localhost:8000/health | |
| **Swagger UI** | http://localhost:8000/docs | Documentação interativa |
| ReDoc | http://localhost:8000/redoc | Documentação alternativa |
| Métricas (Prometheus) | http://localhost:8000/metrics | Exposto pela API |
| **Prometheus** | http://localhost:9090 | |
| **Grafana** | http://localhost:3000 | Dashboard "Ludoteca API" |
| **RabbitMQ (Management)** | http://localhost:15672 | UI de gerenciamento |
| RabbitMQ (AMQP) | localhost:5672 | Porta de mensagens |
| MySQL | localhost:3306 | |

> **Nota:** estas URLs `localhost` referem-se ao localhost da máquina onde o
> Docker Compose está rodando, não necessariamente à sua máquina local. Para
> acessar remotamente, baixe os arquivos e execute a aplicação no seu sistema.

---

## 🔐 Credenciais Padrão dos Serviços

| Serviço | Usuário | Senha |
|---------|---------|-------|
| MySQL (app) | `ludoteca_user` | `ludoteca_pass` |
| MySQL (root) | `root` | `root` |
| RabbitMQ | `guest` | `guest` |
| Grafana | `admin` | `admin` |
| JWT Secret | `super_secret_key_change_me_in_production` | (trocar em produção) |

> ⚠️ Estas credenciais são para **desenvolvimento**. Altere todas antes de
> qualquer uso em produção.

---

## 📁 Estrutura do Projeto

```
projeto_final_backend/
├── Dockerfile                 # Build multi-stage da API
├── .dockerignore
├── .env.example               # Modelo de variáveis de ambiente
├── README.md
├── PROJETO_COMPLETO.md        # Inventário completo do que foi implementado
├── pytest.ini
├── docs/                      # Documentação de arquitetura, modelagem, requisitos
│   ├── arquitetura/
│   ├── database/schema.sql    # Schema MySQL (aplicado no boot do container)
│   ├── diagramas/
│   ├── modelagem/
│   └── requisitos/
├── infra/                     # Infraestrutura
│   ├── docker-compose.yml     # Orquestração: api, mysql, rabbitmq, prometheus, grafana
│   ├── prometheus/prometheus.yml
│   └── grafana/provisioning/  # Datasources e dashboards provisionados
├── src/
│   ├── main.py                # Entrypoint FastAPI (CORS, AOP, métricas, lifespan)
│   ├── requirements.txt
│   └── app/
│       ├── api/v1/            # Controllers (auth, users, games, parties, members, messages, audit)
│       ├── core/              # config, database, security (JWT), aspects (AOP)
│       ├── internal/          # factory, rabbitmq (producer/consumer), events
│       ├── models/            # Modelos SQLAlchemy
│       ├── repositories/      # Repository Pattern (CRUD)
│       ├── schemas/           # Schemas Pydantic
│       └── services/          # Regras de negócio
└── tests/                     # Testes pytest (auth, parties)
```

**Camadas:** `API (Controllers)` → `Services (regras de negócio)` →
`Repositories (acesso a dados)` → `Models (SQLAlchemy)`, com `Schemas` para
validação/serialização e `Core/Internal` para infraestrutura transversal.

---

## 🧩 Design Patterns Implementados

| Pattern | Onde | Descrição |
|---------|------|-----------|
| **Repository** | `src/app/repositories/` | `BaseRepository` genérico com CRUD; repositórios específicos por entidade encapsulam o acesso ao banco. |
| **Factory** | `src/app/internal/factory.py` | `ServiceFactory` instancia todos os Services injetando a sessão do banco. |
| **Dependency Injection** | FastAPI `Depends` | Sessão de banco, usuário autenticado e factory injetados nos controllers. |
| **Service Layer** | `src/app/services/` | Centraliza as regras de negócio, isolando-as dos controllers. |
| **DTO / Schema** | `src/app/schemas/` | Pydantic separa modelos de domínio dos contratos da API. |
| **AOP (Aspectos)** | `src/app/core/aspects.py` | Decorators transversais: `audit_action`, `log_execution`, `require_active_user`, `require_role`. |
| **Middleware (Interceptor)** | `src/main.py` | `logging_aspect` registra método, rota, status e latência de cada request. |
| **Publish/Subscribe (Event-Driven)** | `src/app/internal/rabbitmq.py` + `events.py` | Producer publica eventos de domínio; consumer processa eventos da fila `ludoteca.events`. |
| **Singleton (Settings)** | `src/app/core/config.py` | Configuração única carregada via pydantic-settings. |

---

## 👥 Autores

Vitor Dantas de Almeida Matos
Miguel Colares dos Santos Linard
Rebeca Veras de Lima Sena