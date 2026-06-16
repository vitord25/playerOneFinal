from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.audit_log import AuditAction, AuditLog
from src.app.repositories.audit_log_repository import AuditLogRepository
from src.app.internal import publish_event, LudotecaEvent


class AuditService:
    def __init__(self, db: Session):
        self.repo = AuditLogRepository(db)

    async def log(
        self,
        entity: str,
        entity_id: int,
        action: AuditAction,
        user_id: Optional[int] = None,
        details: Optional[dict] = None,
    ) -> AuditLog:
        # Persiste no banco
        audit_log = self.repo.log(
            entity=entity,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            details=details,
        )

        # Publica evento assíncrono no RabbitMQ
        await publish_event(
            LudotecaEvent.AUDIT_ACTION,
            {
                "entity": entity,
                "entity_id": entity_id,
                "action": action.value,  # serializa o enum como string
                "user_id": user_id,
                "details": details,
            },
        )

        return audit_log