from datetime import datetime, timedelta
from typing import List, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.app.core.config import settings
from src.app.core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme — aponta para o endpoint de login (relativo ao prefixo /api/v1)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


# -----------------------------------------------------------------------------
# Dependency: get_current_user
# Valida o JWT do header Authorization, busca o usuário no banco e o retorna.
# Lança 401 se o token for inválido/expirado ou o usuário não existir,
# e 403 se o usuário estiver inativo.
# -----------------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Import local para evitar dependência circular (models -> database -> ...)
    from src.app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    if user is None:
        raise credentials_exception

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Acesso negado.",
        )

    return user


# -----------------------------------------------------------------------------
# Dependency factory: require_role
# Retorna uma dependency que verifica se o usuário autenticado possui um dos
# papéis permitidos. Lança 403 caso contrário.
#
# Uso: dependencies=[Depends(require_role([UserRole.ADMIN]))]
# -----------------------------------------------------------------------------
def require_role(allowed_roles: List[Union[str, "object"]]):
    # Normaliza os roles permitidos para seus valores string (aceita enum ou str)
    normalized_roles = {
        getattr(role, "value", role) for role in allowed_roles
    }

    def role_checker(current_user=Depends(get_current_user)):
        user_role = getattr(current_user.role, "value", current_user.role)
        if user_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Acesso negado. Requer um dos papéis: "
                    f"{', '.join(sorted(normalized_roles))}"
                ),
            )
        return current_user

    return role_checker