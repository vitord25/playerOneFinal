# =============================================================================
# Dockerfile — API Ludoteca (multi-stage, production-ready)
# Build a partir da raiz do projeto:
#   docker build -t ludoteca-api .
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1 — Builder: instala dependências em um virtualenv isolado
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependências de sistema necessárias para compilar alguns pacotes
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Cria um virtualenv dedicado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala as dependências Python
COPY src/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt


# -----------------------------------------------------------------------------
# Stage 2 — Runtime: imagem final enxuta, sem ferramentas de build
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Cria usuário não-root para rodar a aplicação
RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

# Copia o virtualenv pronto do builder
COPY --from=builder /opt/venv /opt/venv

# Copia o código-fonte da aplicação
COPY src/ /app/src/

# Permissões para o usuário não-root
RUN chown -R app:app /app
USER app

EXPOSE 8000

# Healthcheck simples batendo no endpoint /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').status==200 else sys.exit(1)" || exit 1

# Sobe a API com Uvicorn (produção: sem --reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
