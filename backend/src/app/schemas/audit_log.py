from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any
from src.app.models.audit_log import AuditAction


class AuditLogResponse(BaseModel):
    id: int = Field(..., description="Identificador único do log")
    entity: str = Field(..., description="Entidade auditada (USER, GAME, PARTY, etc)")
    entity_id: int = Field(..., description="ID do objeto auditado")
    action: AuditAction = Field(..., description="Tipo de ação realizada (CREATE, UPDATE, DELETE, etc)")
    details: Optional[Any] = Field(None, description="Detalhes adicionais da ação em formato JSON")
    user_id: Optional[int] = Field(None, description="ID do usuário que realizou a ação (null se sistema)")
    created_at: datetime = Field(..., description="Data e hora em que a ação foi registrada")

    model_config = {
        "from_attributes": True
    }