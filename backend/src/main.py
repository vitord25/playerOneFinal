"""
Ponto de entrada da aplicação FastAPI — Sistema Ludoteca.

Execução em desenvolvimento:
    uvicorn src.main:app --reload

Funcionalidades configuradas aqui:
    - Inicialização do app com metadados (title/description/version)
    - CORS
    - Middleware de logging de requisições (LoggingAspect)
    - Registro de todos os routers de api/v1
    - Health check (GET /health) e raiz (GET /)
    - Métricas Prometheus (GET /metrics)
    - Consumer RabbitMQ em background task (startup/shutdown via lifespan)
    - Criação de tabelas em startup (best-effort, não derruba o boot)
    - Tratamento global de exceções
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.app.core.config import settings
from src.app.core.database import Base, engine
from src.app import models  # noqa: F401  (registra os modelos no metadata)
from src.app.api import api_router
from src.app.internal.rabbitmq import start_consumer, stop_consumer

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("ludoteca")

# Referência à background task do consumer (para cancelar no shutdown)
_consumer_task: asyncio.Task | None = None


# -----------------------------------------------------------------------------
# Lifespan — substitui os eventos startup/shutdown
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _consumer_task

    # --- STARTUP ---
    logger.info("[STARTUP] Inicializando aplicação '%s'...", settings.APP_NAME)

    # Cria as tabelas (best-effort: não derruba o app se o banco estiver indisponível)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("[STARTUP] Tabelas verificadas/criadas no banco de dados.")
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[STARTUP] Não foi possível criar/verificar as tabelas agora: %s", exc
        )

    # Inicia o consumer RabbitMQ como background task
    _consumer_task = asyncio.create_task(start_consumer())
    logger.info("[STARTUP] Background task do consumer RabbitMQ agendada.")

    yield

    # --- SHUTDOWN ---
    logger.info("[SHUTDOWN] Encerrando aplicação...")
    if _consumer_task:
        _consumer_task.cancel()
        try:
            await _consumer_task
        except asyncio.CancelledError:
            pass
    await stop_consumer()
    logger.info("[SHUTDOWN] Recursos liberados.")


# -----------------------------------------------------------------------------
# Aplicação FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API do sistema de gerenciamento de ludoteca universitária. "
        "Gerencia usuários, jogos, parties, membros, mensagens e auditoria."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para os domínios do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Middleware de logging de requisições (LoggingAspect)
# Registra método, caminho, status e tempo de resposta de cada requisição.
# -----------------------------------------------------------------------------
@app.middleware("http")
async def logging_aspect(request: Request, call_next):
    start = time.perf_counter()
    logger.info("[REQ] --> %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        elapsed = (time.perf_counter() - start) * 1000
        logger.exception(
            "[REQ] !! %s %s falhou após %.2fms", request.method, request.url.path, elapsed
        )
        raise
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "[REQ] <-- %s %s | status=%s | %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    response.headers["X-Process-Time-ms"] = f"{elapsed:.2f}"
    return response


# -----------------------------------------------------------------------------
# Métricas Prometheus — expõe GET /metrics
# -----------------------------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["Monitoring"])


# -----------------------------------------------------------------------------
# Routers da API (v1)
# -----------------------------------------------------------------------------
app.include_router(api_router, prefix="/api/v1")


# -----------------------------------------------------------------------------
# Endpoints utilitários
# -----------------------------------------------------------------------------
@app.get("/", tags=["Health"], summary="Raiz da API")
def root():
    return {"status": "online", "app": settings.APP_NAME, "docs": "/docs"}


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "1.0.0"}


# -----------------------------------------------------------------------------
# Tratamento global de exceções
# -----------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("[ERROR] Exceção não tratada em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor."},
    )


# -----------------------------------------------------------------------------
# Execução direta (python -m src.main)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
