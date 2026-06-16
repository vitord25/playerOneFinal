from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, description="Conteúdo da mensagem")


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int = Field(..., description="Identificador único da mensagem")
    user_id: int = Field(..., description="ID do usuário que enviou a mensagem")
    party_id: int = Field(..., description="ID da party à qual a mensagem pertence")
    created_at: datetime = Field(..., description="Data e hora de envio da mensagem")

    model_config = {
        "from_attributes": True
    }