from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.app.core.database import get_db
from src.app.core.security import get_current_user, require_role
from src.app.models.user import User, UserRole
from src.app.schemas.party_member import PartyMemberResponse
from src.app.internal.factory import get_factory

router = APIRouter()


# ─────────────────────────────────────────────
# POST /parties/{party_id}/members — RF17 | Autenticado
# Solicitar entrada na party
# ─────────────────────────────────────────────
@router.post(
    "/{party_id}/members",
    response_model=PartyMemberResponse,
    status_code=201,
    summary="Solicitar entrada na party",
)
async def request_membership(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_member_service().request_join(
        party_id, current_user
    )


# ─────────────────────────────────────────────
# GET /parties/{party_id}/members — RF18 | Organizador ou Admin
# Listar membros de uma party
# AOP: require_ownership_or_admin verificado no service
# ─────────────────────────────────────────────
@router.get(
    "/{party_id}/members",
    response_model=List[PartyMemberResponse],
    summary="Listar membros da party (Organizador ou Admin)",
)
async def list_members(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_member_service().get_by_party(party_id)


# ─────────────────────────────────────────────
# PATCH /parties/{party_id}/members/{member_id}/approve — RF19 | Organizador
# Aprovar solicitação de membro
# AOP: require_ownership verificado no service
# ─────────────────────────────────────────────
@router.patch(
    "/{party_id}/members/{member_id}/approve",
    response_model=PartyMemberResponse,
    summary="Aprovar membro na party (Organizador)",
)
async def approve_member(
    party_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_member_service().approve_member(
        member_id, current_user
    )


# ─────────────────────────────────────────────
# PATCH /parties/{party_id}/members/{member_id}/reject — RF19 | Organizador
# Rejeitar solicitação de membro
# AOP: require_ownership verificado no service
# ─────────────────────────────────────────────
@router.patch(
    "/{party_id}/members/{member_id}/reject",
    response_model=PartyMemberResponse,
    summary="Rejeitar membro da party (Organizador)",
)
async def reject_member(
    party_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_member_service().reject_member(
        member_id, current_user
    )


# ─────────────────────────────────────────────
# DELETE /parties/{party_id}/members/me — RF17 | Autenticado
# Sair da party voluntariamente.
# IMPORTANTE: declarada ANTES da rota /{member_id} para que o caminho
# literal "me" não seja interpretado como um member_id.
# ─────────────────────────────────────────────
@router.delete(
    "/{party_id}/members/me",
    status_code=204,
    summary="Sair da party",
)
async def leave_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).party_member_service().leave_party(
        party_id, current_user
    )


# ─────────────────────────────────────────────
# DELETE /parties/{party_id}/members/{member_id} — RF19 | Organizador ou Admin
# Remover membro da party
# AOP: require_ownership_or_admin verificado no service
# ─────────────────────────────────────────────
@router.delete(
    "/{party_id}/members/{member_id}",
    status_code=204,
    summary="Remover membro da party (Organizador ou Admin)",
)
async def remove_member(
    party_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).party_member_service().remove_member(
        member_id, current_user
    )