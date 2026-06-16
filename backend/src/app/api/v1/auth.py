"""
Router de Autenticação (RF20 / RF22).

Endpoints:
    POST /auth/register  — registro de novos usuários (público)
    POST /auth/login     — autenticação (OAuth2 password flow) → JWT
    POST /auth/refresh   — renova o token de acesso do usuário autenticado
    POST /auth/logout    — registra o logout (auditoria)
    GET  /auth/me        — retorna o usuário autenticado
"""
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.app.core.database import get_db
from src.app.core.security import create_access_token, get_current_user
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserResponse
from src.app.internal.factory import get_factory

router = APIRouter()


# ─────────────────────────────────────────────
# Schema do token de resposta
# ─────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─────────────────────────────────────────────
# POST /auth/register — RF20 | Público
# Registro de novo usuário (sempre nasce como USER)
# ─────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().create_user(user_in)


# ─────────────────────────────────────────────
# POST /auth/login — RF22 | Público
# Autenticação via OAuth2 password flow.
# O campo `username` do formulário recebe o e-mail do usuário.
# ─────────────────────────────────────────────
@router.post(
    "/login",
    response_model=Token,
    summary="Autenticar usuário e obter token JWT",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    access_token = await get_factory(db).user_service().authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    return Token(access_token=access_token, token_type="bearer")


# ─────────────────────────────────────────────
# POST /auth/refresh — Autenticado
# Renova o token de acesso a partir de um token ainda válido.
# ─────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar token de acesso",
)
async def refresh(
    current_user: User = Depends(get_current_user),
):
    access_token = create_access_token(
        {"sub": str(current_user.id), "role": current_user.role.value}
    )
    return Token(access_token=access_token, token_type="bearer")


# ─────────────────────────────────────────────
# POST /auth/logout — Autenticado
# Registra o logout em auditoria (JWT é stateless).
# ─────────────────────────────────────────────
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Encerrar sessão (registra auditoria)",
)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).user_service().logout(current_user)


# ─────────────────────────────────────────────
# GET /auth/me — Autenticado
# Retorna os dados do usuário autenticado.
# ─────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter usuário autenticado",
)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user
