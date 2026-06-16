from typing import List, Optional
from sqlalchemy.orm import Session

from src.app.models.user import User
from src.app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    # RF24 - Apenas usuários ativos
    def get_active_users(self) -> List[User]:
        return (
            self.db.query(User)
            .filter(User.active == True)
            .all()
        )

    # RF25 - Todos os usuários incluindo inativos (Admin)
    def get_all_with_inactive(self) -> List[User]:
        return self.db.query(User).all()