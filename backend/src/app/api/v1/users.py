from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.app.core.database import get_db
from src.app.core.security import get_current_user, require_role
from src.app.models.user import User, UserRole
from src.app.schemas.user import UserResponse, UserUpdate, UserChangePassword, UserRoleUpdate
from src.app.internal.factory import get_factory

router = APIRouter()


# ─────────────────────────────────────────────
# GET /users — RF25 | Admin
# ─────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Listar todos os usuários (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def list_users(
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().get_all()


# ─────────────────────────────────────────────
# GET /users/active — RF24 | Admin
# ─────────────────────────────────────────────
@router.get(
    "/active",
    response_model=List[UserResponse],
    summary="Listar usuários ativos (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def list_active_users(
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().get_active_users()


# ─────────────────────────────────────────────
# GET /users/me — RF23 | Autenticado
# ─────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter perfil do usuário autenticado",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ─────────────────────────────────────────────
# GET /users/{user_id} — RF23 | Admin
# ─────────────────────────────────────────────
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Buscar usuário por ID (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().get_by_id(user_id)


# ─────────────────────────────────────────────
# PATCH /users/me — RF21 | Autenticado
# ─────────────────────────────────────────────
@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Atualizar próprio perfil",
)
async def update_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().update_user(
        current_user.id, user_in, current_user
    )


# ─────────────────────────────────────────────
# PATCH /users/me/password — RF21 | Autenticado
# ─────────────────────────────────────────────
@router.patch(
    "/me/password",
    status_code=204,
    summary="Alterar própria senha",
)
async def change_password(
    body: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).user_service().change_password(
        user_id=current_user.id,
        current_password=body.current_password,
        new_password=body.new_password,
        current_user=current_user,
    )


# ─────────────────────────────────────────────
# PATCH /users/{user_id}/role — RF26 | Admin
# ─────────────────────────────────────────────
@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Alterar role de usuário (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def change_role(
    user_id: int,
    body: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().change_role(
        user_id, body.role, current_user
    )


# ─────────────────────────────────────────────
# DELETE /users/{user_id} — RF27 | Admin
# ─────────────────────────────────────────────
@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Desativar usuário (Admin / soft delete)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().deactivate_user(user_id, current_user)


# ─────────────────────────────────────────────
# PATCH /users/{user_id}/reactivate — RF28 | Admin
# ─────────────────────────────────────────────
@router.patch(
    "/{user_id}/reactivate",
    response_model=UserResponse,
    summary="Reativar usuário (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def reactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).user_service().reactivate_user(user_id, current_user)