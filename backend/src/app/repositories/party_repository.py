from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.app.models.party import Party, PartyStatus
from src.app.models.party_member import PartyMember, PartyMemberStatus
from src.app.repositories.base_repository import BaseRepository


class PartyRepository(BaseRepository[Party]):
    def __init__(self, db: Session):
        super().__init__(Party, db)

    # -------------------------------------------------------------------------
    # RF11 - Parties disponíveis / RF29 - Parties por status (Admin)
    # -------------------------------------------------------------------------
    def get_by_status(self, status: PartyStatus) -> List[Party]:
        return (
            self.db.query(Party)
            .filter(Party.status == status)
            .all()
        )

    # -------------------------------------------------------------------------
    # RF10 - Parties do usuário (como organizador ou membro aprovado)
    # -------------------------------------------------------------------------
    def get_by_member_or_organizer(self, user_id: int) -> List[Party]:
        return (
            self.db.query(Party)
            .outerjoin(PartyMember, and_(
                PartyMember.party_id == Party.id,
                PartyMember.user_id == user_id,
                PartyMember.status == PartyMemberStatus.APPROVED,
            ))
            .filter(or_(
                Party.organizer_id == user_id,
                PartyMember.user_id == user_id,
            ))
            .distinct()
            .all()
        )

    # -------------------------------------------------------------------------
    # RN10 - Verifica se organizador já tem party PENDING ou APPROVED
    # -------------------------------------------------------------------------
    def get_active_by_organizer(self, organizer_id: int) -> Optional[Party]:
        return (
            self.db.query(Party)
            .filter(
                Party.organizer_id == organizer_id,
                Party.status.in_([PartyStatus.PENDING, PartyStatus.APPROVED]),
            )
            .first()
        )


    def get_active_by_organizer_all(self, organizer_id: int) -> List[Party]:
        return (
            self.db.query(Party)
            .filter(
                Party.organizer_id == organizer_id,
                Party.status.in_([PartyStatus.PENDING, PartyStatus.APPROVED]),
            )
            .all()
        )

    # -------------------------------------------------------------------------
    # RN09 - Verifica se organizador já tem party ativa com o mesmo jogo
    # -------------------------------------------------------------------------
    def get_active_by_organizer_and_game(
        self, organizer_id: int, game_id: int
    ) -> Optional[Party]:
        return (
            self.db.query(Party)
            .filter(
                Party.organizer_id == organizer_id,
                Party.game_id == game_id,
                Party.status.in_([PartyStatus.PENDING, PartyStatus.APPROVED]),
            )
            .first()
        )

    # -------------------------------------------------------------------------
    # RN06 / RN07 - Busca parties ativas de um jogo específico
    # -------------------------------------------------------------------------
    def get_active_by_game(self, game_id: int) -> List[Party]:
        return (
            self.db.query(Party)
            .filter(
                Party.game_id == game_id,
                Party.status.in_([PartyStatus.PENDING, PartyStatus.APPROVED]),
            )
            .all()
        )

    # -------------------------------------------------------------------------
    # RN12 - Conta parties ativas de um jogo (para verificar cópias disponíveis)
    # -------------------------------------------------------------------------
    def count_active_by_game(self, game_id: int) -> int:
        return (
            self.db.query(Party)
            .filter(
                Party.game_id == game_id,
                Party.status.in_([PartyStatus.PENDING, PartyStatus.APPROVED]),
            )
            .count()
        )

    # -------------------------------------------------------------------------
    # RN20 - Busca parties rejeitadas há mais de X dias
    # -------------------------------------------------------------------------
    def get_old_rejected_parties(self, limit_date: datetime) -> List[Party]:
        return (
            self.db.query(Party)
            .filter(
                Party.status == PartyStatus.REJECTED,
                Party.updated_at <= limit_date,
            )
            .all()
        )