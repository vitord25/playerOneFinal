from sqlalchemy.orm import Session
from src.app.services.user_service import UserService
from src.app.services.game_service import GameService
from src.app.services.party_service import PartyService
from src.app.services.party_member_service import PartyMemberService
from src.app.services.message_service import MessageService
from src.app.services.audit_service import AuditService


class ServiceFactory:
    """
    Factory Central responsável por instanciar todos os Services
    injetando a sessão do banco de dados como dependência.
    Implementa o Factory Pattern.
    """

    def __init__(self, db: Session):
        self.db = db

    def user_service(self) -> UserService:
        return UserService(self.db)

    def game_service(self) -> GameService:
        return GameService(self.db)

    def party_service(self) -> PartyService:
        return PartyService(self.db)

    def party_member_service(self) -> PartyMemberService:
        return PartyMemberService(self.db)

    def message_service(self) -> MessageService:
        return MessageService(self.db)

    def audit_service(self) -> AuditService:
        return AuditService(self.db)


def get_factory(db: Session) -> ServiceFactory:
    return ServiceFactory(db)