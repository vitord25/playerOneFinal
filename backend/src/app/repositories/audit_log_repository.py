from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from src.app.models.audit_log import AuditLog, AuditAction
from src.app.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    # -------------------------------------------------------------------------
    # Persistência direta — não usa o create() do BaseRepository
    # para manter controle total sobre os campos
    # -------------------------------------------------------------------------
    def log(
        self,
        entity: str,
        entity_id: int,
        action: AuditAction,
        user_id: Optional[int],
        details: Optional[dict] = None,
    ) -> AuditLog:
        audit = AuditLog(
            entity=entity,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            details=details,
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    # -------------------------------------------------------------------------
    # Histórico de uma entidade específica (ex: todos os eventos de PARTY id=5)
    # -------------------------------------------------------------------------
    def get_by_entity(self, entity: str, entity_id: int) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity == entity,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Histórico de ações de um usuário específico
    # -------------------------------------------------------------------------
    def get_by_user(self, user_id: int) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Histórico por tipo de ação (ex: todos os LOGINs)
    # -------------------------------------------------------------------------
    def get_by_action(self, action: AuditAction) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Filtro combinado — útil para admin dashboard
    # Todos os parâmetros são opcionais
    # -------------------------------------------------------------------------
    def get_filtered(
        self,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        user_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog)

        if entity:
            query = query.filter(AuditLog.entity == entity)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if date_from:
            query = query.filter(AuditLog.created_at >= date_from)
        if date_to:
            query = query.filter(AuditLog.created_at <= date_to)

        return (
            query
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )