# 🎲 Ludoteca — Instruções de Execução

Sistema de gerenciamento de ludoteca universitária com **frontend React (Vite)** unificado e **backend FastAPI**.

Este documento explica como rodar o **backend** e o **frontend**, resume as **correções aplicadas** e lista as **funcionalidades implementadas**.

> ⚠️ **Nota sobre `localhost`:** Os endereços `localhost`/`127.0.0.1` citados aqui referem-se à máquina onde você for executar a aplicação. Caso este projeto tenha sido preparado no computador do Abacus AI Agent, esse `localhost` é o da VM do agente, **não** o da sua máquina. Para rodar localmente, baixe todos os arquivos pelo ícone **"Files"** no canto superior direito, entre na pasta baixada e siga os passos abaixo no seu próprio sistema.

---

## 📁 Estrutura do Projeto

```
projeto/
├── frontend_final/                      # Frontend unificado (React + Vite)  ← USE ESTE
└── backend_extract/
    └── projeto_final_backend/           # Backend (FastAPI)
        ├── infra/docker-compose.yml     # Sobe API + MySQL + RabbitMQ + Grafana/Prometheus
        ├── run_local_sqlite.py          # Execução rápida sem Docker (SQLite)
        └── src/main.py                  # Entrada da API
```

---

## 🚀 1. Executando o Backend

A API expõe os endpoints sob o prefixo **`/api/v1`** e roda em **`http://localhost:8000`** (Swagger em `http://localhost:8000/docs`).

### Opção A — Docker Compose (recomendado / produção-like)

Sobe a stack completa: **API (FastAPI)**, **MySQL 8**, **RabbitMQ** e o monitoramento (Grafana/Prometheus).

```bash
cd projeto/backend_extract/projeto_final_backend/infra
docker compose up --build        # ou: docker-compose up --build
```

Serviços expostos:

| Serviço     | URL / Porta                       | Credenciais                     |
|-------------|-----------------------------------|---------------------------------|
| API         | http://localhost:8000  (`/docs`)  | —                               |
| MySQL       | localhost:3306                    | `ludoteca_user` / `ludoteca_pass` |
| RabbitMQ    | http://localhost:15672 (painel)   | `guest` / `guest`               |
| Grafana     | http://localhost:3001             | conforme `infra/grafana`        |
| Prometheus  | http://localhost:9090             | —                               |

Para parar: `Ctrl+C` e depois `docker compose down`.

### Opção B — Execução local rápida com SQLite (sem Docker)

Útil para desenvolvimento/teste rápido, sem precisar de MySQL nem RabbitMQ (o RabbitMQ falha de forma silenciosa e não derruba a aplicação).

```bash
cd projeto/backend_extract/projeto_final_backend
python -m venv .venv && source .venv/bin/activate     # se ainda não tiver a venv
pip install -r requirements.txt                        # ou as deps já instaladas na .venv
python run_local_sqlite.py
```

Isso cria um arquivo `local_dev.db` (SQLite) e sobe a API em `http://localhost:8000`.

> Este modo foi usado para **validar o fluxo completo de integração** (ver seção "Validação").

---

## 💻 2. Executando o Frontend

```bash
cd projeto/frontend_final
npm install
npm run dev
```

O Vite sobe o frontend em **`http://localhost:5173`** (porta padrão do Vite).

### Configuração da URL da API

O frontend lê a URL do backend da variável **`VITE_API_URL`** (arquivo `.env`):

```env
# projeto/frontend_final/.env
VITE_API_URL=http://localhost:8000
```

Se o backend estiver em outro endereço/porta, ajuste essa variável e reinicie o `npm run dev`.

Para build de produção:

```bash
npm run build      # gera a pasta dist/
npm run preview    # serve o build localmente
```

---

## 👤 3. Primeiro acesso / Criando um Administrador

O cadastro público cria usuários com papel **`USER`** (aluno). O **Dashboard Administrativo** exige papel **`ADMIN`**.

Para promover o primeiro administrador:

**Com Docker (MySQL):**
```bash
docker exec -it ludoteca_mysql mysql -uludoteca_user -pludoteca_pass ludoteca \
  -e "UPDATE users SET role='ADMIN' WHERE email='seu_email@exemplo.com';"
```

**Com SQLite (run_local_sqlite.py):**
```bash
sqlite3 local_dev.db "UPDATE users SET role='ADMIN' WHERE email='seu_email@exemplo.com';"
```

Depois faça login normalmente — usuários `ADMIN` são redirecionados automaticamente para `/admin/dashboard`.

---

## 🔧 4. Correções Aplicadas na Unificação

A unificação usou a **interface visual da versão `main` (Player_One)** como base e integrou a **camada de serviços/API da versão `feat`**. Principais correções:

1. **Bug `process.env` → `import.meta.env`**
   O cliente HTTP usava `process.env.REACT_APP_API_URL` (padrão Create-React-App), que **não funciona no Vite** e resultava em `undefined`. Corrigido para `import.meta.env.VITE_API_URL` em `src/services/api.js`.

2. **Login por e-mail (não por matrícula)**
   Ambos os frontends antigos enviavam `matricula` no login, mas o backend autentica por **e-mail** (OAuth2 `username` = e-mail, `application/x-www-form-urlencoded`). As telas de Login/Cadastro foram reescritas para usar **nome + e-mail + senha**.

3. **Autenticação JWT centralizada**
   - `src/services/api.js`: instância axios com **interceptor de request** que injeta `Authorization: Bearer <token>` e **interceptor de response 401** que tenta refresh e redireciona ao login.
   - `src/context/AuthContext.jsx`: contexto global (`useAuth`) com `login`, `register`, `logout`, `refreshUser`, `user`, `isAuthenticated`, `isAdmin`.
   - `src/components/ProtectedRoute.jsx`: guarda de rotas autenticadas, com flag `adminOnly` para o painel admin.

4. **Adaptadores de dados (backend → UI)**
   `src/services/adapters.js` traduz os campos do backend (em inglês) para os campos esperados pela UI em português (`nome`, `categoria`, `faixaEtaria`, `minJogadores`, `maxJogadores`, `duracao`, `quantidadeDisponivel`, `statusJogo`, etc.), incluindo imagem-placeholder por categoria.

5. **Padronização de rotas com barra final**
   Endpoints de coleção do backend exigem barra final (ex.: `/api/v1/games/`, `/api/v1/parties/`). Os serviços foram padronizados para evitar redirecionamentos `307`.

6. **Painel administrativo reescrito**
   As páginas admin da versão `feat` importavam arquivos inexistentes (estavam quebradas). Foram reescritas de forma limpa e integradas às rotas e ao tema visual.

7. **Limpeza de mocks**
   Removido o serviço mock antigo (`src/service/` com `JogoApi` fake) — todas as telas agora consomem a API real.

---

## ✅ 5. Funcionalidades Implementadas

### Aluno (papel `USER`)
- **Cadastro e Login** com validação de senha forte (RGN03).
- **Home / Catálogo de jogos** — lista jogos disponíveis (`/games/available`).
- **Detalhe do jogo** — informações completas do jogo.
- **Criar Party (mesa)** — agendar partida (jogo, descrição, data, hora, local, nº máx. de jogadores).
- **Lista de Parties abertas** — solicitar participação.
- **Minhas Parties** — separa parties que organizo e que participo; mostra solicitações pendentes.
- **Detalhe da Party + Chat** — aprovar/recusar/remover membros (organizador), entrar/sair, cancelar, e **chat em tempo real** (envio e listagem de mensagens).
- **Perfil** — editar dados e logout.

### Administrador (papel `ADMIN`)
- **Dashboard** — estatísticas (parties ativas, jogos, usuários).
- **Gerenciar Jogos** — CRUD completo + alternar disponibilidade.
- **Gerenciar Usuários** — alterar papel, desativar/reativar.
- **Gerenciar Parties** — aprovar/recusar/cancelar/excluir, com filtro por status.

---

## 🧪 6. Validação da Integração

O fluxo ponta-a-ponta foi **testado com sucesso** contra o backend real (modo SQLite):

```
✔ Health check
✔ Cadastro de usuário
✔ Login (JWT emitido)
✔ Criação de jogo (admin)
✔ Listagem de jogos
✔ Criação de party
✔ Aprovação da party (admin)
✔ Listagem de parties abertas
✔ Solicitação de participação (2º jogador)
✔ Aprovação de membro (organizador)
✔ Envio e listagem de mensagens (chat)
```

E o frontend compila sem erros: `npm run build` ✔.

---

## 📦 Resumo dos comandos

```bash
# Backend (Docker)
cd projeto/backend_extract/projeto_final_backend/infra && docker compose up --build

# Backend (rápido, SQLite)
cd projeto/backend_extract/projeto_final_backend && python run_local_sqlite.py

# Frontend
cd projeto/frontend_final && npm install && npm run dev
```

Bom jogo! 🎲
