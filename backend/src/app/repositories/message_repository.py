from typing import List
from sqlalchemy.orm import Session

from src.app.models.message import Message
from src.app.repositories.base_repository import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: Session):
        super().__init__(Message, db)

    # RF21 - Mensagens de uma party ordenadas por created_at ASC
    # skip/limit para paginação futura
    def get_by_party(
        self, party_id: int, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.party_id == party_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Histórico de mensagens de um usuário (útil para auditoria/admin)
    def get_by_user(self, user_id: int) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.created_at.asc())
            .all()
        )