from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from src.app.core.database import get_db
from src.app.core.security import get_current_user, require_role
from src.app.models.user import User, UserRole
from src.app.schemas.message import MessageCreate, MessageResponse
from src.app.internal.factory import get_factory

router = APIRouter()


# ─────────────────────────────────────────────
# POST /parties/{party_id}/messages — RF20 | Membro Aprovado
# Enviar mensagem na party
# ─────────────────────────────────────────────
@router.post(
    "/{party_id}/messages",
    response_model=MessageResponse,
    status_code=201,
    summary="Enviar mensagem na party (Membro Aprovado)",
)
async def send_message(
    party_id: int,
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).message_service().send_message(
        party_id, message_in, current_user
    )


# ─────────────────────────────────────────────
# GET /parties/{party_id}/messages — RF21 | Membro Aprovado ou Admin
# Listar mensagens da party com paginação
# ─────────────────────────────────────────────
@router.get(
    "/{party_id}/messages",
    response_model=List[MessageResponse],
    summary="Listar mensagens da party (Membro Aprovado ou Admin)",
)
async def list_messages(
    party_id: int,
    skip: int = Query(default=0, ge=0, description="Número de registros a pular"),
    limit: int = Query(default=100, ge=1, le=500, description="Máximo de registros retornados"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).message_service().get_by_party(
        party_id, current_user, skip=skip, limit=limit
    )


# ─────────────────────────────────────────────
# DELETE /parties/{party_id}/messages/{message_id} — RF22 | Admin
# Moderar / remover mensagem
# ─────────────────────────────────────────────
# OBS: party_id é inrelevante, usado para manter consistencia de rota
@router.delete(
    "/{party_id}/messages/{message_id}",
    status_code=204,
    summary="Deletar mensagem (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def delete_message(
    party_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).message_service().delete_message(message_id, current_user)