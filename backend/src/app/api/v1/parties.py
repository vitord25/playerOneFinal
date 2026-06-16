from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.app.core.database import get_db
from src.app.core.security import get_current_user, require_role
from src.app.models.user import User, UserRole
from src.app.schemas.party import PartyCreate, PartyUpdate, PartyResponse
from src.app.internal.factory import get_factory

router = APIRouter()


# ─────────────────────────────────────────────
# POST /parties — RF08 | Autenticado
# ─────────────────────────────────────────────
@router.post(
    "/",
    response_model=PartyResponse,
    status_code=201,
    summary="Criar nova party",
)
async def create_party(
    party_in: PartyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().create_party(party_in, current_user)


# ─────────────────────────────────────────────
# GET /parties — RF09 | Admin
# ─────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[PartyResponse],
    summary="Listar todas as parties (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def list_all_parties(
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().get_all()


# ─────────────────────────────────────────────
# GET /parties/open — RF10 | Autenticado
# Parties abertas para solicitação de entrada
# ─────────────────────────────────────────────
@router.get(
    "/open",
    response_model=List[PartyResponse],
    summary="Listar parties abertas",
)
async def list_open_parties(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await get_factory(db).party_service().get_open_parties()


# ─────────────────────────────────────────────
# GET /parties/my — RF11 | Autenticado
# Parties onde o usuário é organizador ou membro aprovado
# ─────────────────────────────────────────────
@router.get(
    "/my",
    response_model=List[PartyResponse],
    summary="Listar minhas parties",
)
async def list_my_parties(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().get_my_parties(current_user.id)


# ─────────────────────────────────────────────
# GET /parties/{party_id} — RF12 | Autenticado
# ─────────────────────────────────────────────
@router.get(
    "/{party_id}",
    response_model=PartyResponse,
    summary="Buscar party por ID",
)
async def get_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().get_by_id(party_id)


# ─────────────────────────────────────────────
# PATCH /parties/{party_id} — RF13 | Organizador
# AOP: require_ownership verificado no service
# ─────────────────────────────────────────────
@router.patch(
    "/{party_id}",
    response_model=PartyResponse,
    summary="Atualizar party (Organizador)",
)
async def update_party(
    party_id: int,
    party_in: PartyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().update_party(
        party_id, party_in, current_user
    )


# ─────────────────────────────────────────────
# PATCH /parties/{party_id}/approve — RF14 | Admin
# ─────────────────────────────────────────────
@router.patch(
    "/{party_id}/approve",
    response_model=PartyResponse,
    summary="Aprovar party (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def approve_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().approve_party(party_id, current_user)


# ─────────────────────────────────────────────
# PATCH /parties/{party_id}/cancel — RF15 | Organizador ou Admin
# AOP: require_ownership_or_admin verificado no service
# ─────────────────────────────────────────────
@router.patch(
    "/{party_id}/cancel",
    response_model=PartyResponse,
    summary="Cancelar party (Organizador ou Admin)",
)
async def cancel_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).party_service().cancel_party(party_id, current_user)


# ─────────────────────────────────────────────
# DELETE /parties/{party_id} — RF16 | Admin
# ─────────────────────────────────────────────
@router.delete(
    "/{party_id}",
    status_code=204,
    summary="Deletar party (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def delete_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).party_service().delete_rejected_party(party_id, current_user)