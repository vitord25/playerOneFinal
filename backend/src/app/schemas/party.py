from datetime import date as date_, time as time_, datetime
from pydantic import BaseModel, Field
from typing import Optional

class PartyBase(BaseModel):
    game_id: int = Field(..., description="ID do jogo associado à party")
    description: str = Field(..., description="Descrição da party")
    date: date_ = Field(..., description="Data de realização da party")
    time: time_ = Field(..., description="Horário de início da party")
    location: str = Field(..., description="Local de realização da party")
    max_players: int = Field(..., gt=0, description="Número máximo de jogadores permitidos")


class PartyCreate(PartyBase):
    pass


class PartyUpdate(BaseModel):
    description: Optional[str] = Field(None, description="Descrição da party")
    date: Optional[date_] = Field(None, description="Data de realização da party")
    time: Optional[time_] = Field(None, description="Horário de início da party")
    location: Optional[str] = Field(None, description="Local de realização da party")
    max_players: Optional[int] = Field(None, gt=0, description="Número máximo de jogadores permitidos")


class PartyResponse(PartyBase):
    id: int = Field(..., description="Identificador único da party")
    organizer_id: int = Field(..., description="ID do usuário organizador da party")
    status: str = Field(..., description="Status atual da party (PENDING, APPROVED, REJECTED, CANCELLED)")
    created_at: datetime = Field(..., description="Data e hora de criação do registro")

    model_config = {
        "from_attributes": True
    }