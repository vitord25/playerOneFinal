from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.app.core.database import get_db
from src.app.core.security import require_role
from src.app.models.user import UserRole
from src.app.models.audit_log import AuditAction, AuditLog
from src.app.schemas.audit_log import AuditLogResponse
from src.app.internal.factory import get_factory

router = APIRouter()

# ─────────────────────────────────────────────
# GET /audit — RF29 | Admin
# Listagem filtrada de logs de auditoria
# ─────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[AuditLogResponse],
    summary="Listar logs de auditoria (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def list_audit_logs(
    entity: Optional[str] = Query(None, description="Filtrar por entidade (GAME, USER, PARTY, etc)"),
    entity_id: Optional[int] = Query(None, description="Filtrar por ID da entidade"),
    action: Optional[AuditAction] = Query(None, description="Filtrar por tipo de ação"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID do usuário que realizou a ação"),
    date_from: Optional[datetime] = Query(None, description="Data inicial (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Data final (ISO 8601)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Retorna o histórico de ações do sistema com filtros avançados.
    Apenas administradores têm acesso a este endpoint.
    """
    return await get_factory(db).audit_service().repo.get_filtered(
        entity=entity,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )

# ─────────────────────────────────────────────
# GET /audit/entity/{entity}/{entity_id} — RF30 | Admin
# Histórico específico de um objeto
# ─────────────────────────────────────────────
@router.get(
    "/entity/{entity}/{entity_id}",
    response_model=List[AuditLogResponse],
    summary="Histórico de auditoria de uma entidade específica (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def get_entity_history(
    entity: str,
    entity_id: int,
    db: Session = Depends(get_db),
):
    return await get_factory(db).audit_service().repo.get_by_entity(entity, entity_id)