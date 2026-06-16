from datetime import datetime
from pydantic import BaseModel, Field


class PartyMemberBase(BaseModel):
    party_id: int = Field(..., description="ID da party à qual o usuário deseja se associar")


class PartyMemberCreate(PartyMemberBase):
    pass


class PartyMemberResponse(PartyMemberBase):
    id: int = Field(..., description="Identificador único do membro")
    user_id: int = Field(..., description="ID do usuário membro")
    status: str = Field(..., description="Status da solicitação (PENDING, APPROVED, REJECTED)")
    joined_at: datetime = Field(..., description="Data e hora da solicitação de entrada")

    model_config = {
        "from_attributes": True
    }