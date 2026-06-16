from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class GameBase(BaseModel):
    name: str = Field(..., description="Nome do jogo")
    description: Optional[str] = Field(None, description="Descrição do jogo")
    minimum_age: int = Field(..., ge=0, description="Idade mínima recomendada para jogar")
    category: str = Field(..., description="Categoria do jogo (ex: Estratégia, RPG)")
    quantity: int = Field(..., gt=0, description="Quantidade de cópias disponíveis na ludoteca")
    min_players: int = Field(..., gt=0, description="Número mínimo de jogadores")
    max_players: int = Field(..., gt=0, description="Número máximo de jogadores")
    min_duration_minutes: int = Field(..., gt=0, description="Duração mínima de uma partida em minutos")
    max_duration_minutes: int = Field(..., gt=0, description="Duração máxima de uma partida em minutos")


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome do jogo")
    description: Optional[str] = Field(None, description="Descrição do jogo")
    available: Optional[bool] = Field(None, description="Indica se o jogo está disponível para reserva")
    quantity: Optional[int] = Field(None, gt=0, description="Quantidade de cópias disponíveis")


class GameResponse(GameBase):
    id: int = Field(..., description="Identificador único do jogo")
    available: bool = Field(..., description="Indica se o jogo está disponível para reserva")
    created_at: datetime = Field(..., description="Data e hora de criação do registro")

    model_config = {
        "from_attributes": True
    }