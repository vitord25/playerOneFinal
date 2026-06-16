from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from src.app.models.user import UserRole

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str

class UserRoleUpdate(BaseModel):
    role: UserRole

class UserBase(BaseModel):
    name: str = Field(..., description="Nome completo do usuário")
    email: EmailStr = Field(..., description="E-mail único do usuário")
    description: Optional[str] = Field(None, description="Descrição ou bio do usuário")
    profile_image_url: Optional[str] = Field(None, description="URL da imagem de perfil")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Senha do usuário (mínimo 6 caracteres)")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome completo do usuário")
    description: Optional[str] = Field(None, description="Descrição ou bio do usuário")
    profile_image_url: Optional[str] = Field(None, description="URL da imagem de perfil")
    active: Optional[bool] = Field(None, description="Status de ativação do usuário")


class UserResponse(UserBase):
    id: int = Field(..., description="Identificador único do usuário")
    role: str = Field(..., description="Papel do usuário no sistema (ADMIN ou USER)")
    active: bool = Field(..., description="Indica se o usuário está ativo")
    created_at: datetime = Field(..., description="Data e hora de criação do registro")

    model_config = {
        "from_attributes": True
    }