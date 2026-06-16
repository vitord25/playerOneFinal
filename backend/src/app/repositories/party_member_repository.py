from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.app.models.party_member import PartyMember, PartyMemberStatus
from src.app.models.party import Party, PartyStatus
from src.app.repositories.base_repository import BaseRepository


class PartyMemberRepository(BaseRepository[PartyMember]):
    def __init__(self, db: Session):
        super().__init__(PartyMember, db)

    # -------------------------------------------------------------------------
    # Já existia - mantido
    # -------------------------------------------------------------------------
    def get_by_user_and_party(self, user_id: int, party_id: int) -> Optional[PartyMember]:
        return (
            self.db.query(PartyMember)
            .filter(
                PartyMember.user_id == user_id,
                PartyMember.party_id == party_id,
            )
            .first()
        )

    def get_by_party(self, party_id: int) -> List[PartyMember]:
        return (
            self.db.query(PartyMember)
            .filter(PartyMember.party_id == party_id)
            .all()
        )

    def get_by_user(self, user_id: int) -> List[PartyMember]:
        return (
            self.db.query(PartyMember)
            .filter(PartyMember.user_id == user_id)
            .all()
        )

    def get_approved_members_count(self, party_id: int) -> int:
        return (
            self.db.query(PartyMember)
            .filter(
                PartyMember.party_id == party_id,
                PartyMember.status == PartyMemberStatus.APPROVED,
            )
            .count()
        )

    def get_pending_by_party(self, party_id: int) -> List[PartyMember]:
        return (
            self.db.query(PartyMember)
            .filter(
                PartyMember.party_id == party_id,
                PartyMember.status == PartyMemberStatus.PENDING,
            )
            .all()
        )

    # -------------------------------------------------------------------------
    # RN13 / RN14 - Verifica conflito de horário para um usuário
    # Retorna membros aprovados do usuário em parties que conflitam com
    # a data/hora da party alvo
    # -------------------------------------------------------------------------
    def get_approved_conflicting(
        self, user_id: int, party_date, party_time
    ) -> List[PartyMember]:
        return (
            self.db.query(PartyMember)
            .join(Party, Party.id == PartyMember.party_id)
            .filter(
                PartyMember.user_id == user_id,
                PartyMember.status == PartyMemberStatus.APPROVED,
                Party.date == party_date,
                Party.time == party_time,
                Party.status == PartyStatus.APPROVED,
            )
            .all()
        )

    # -------------------------------------------------------------------------
    # RN08 - Busca o próximo membro elegível para ser organizador
    # Critérios:
    #   - aprovado na party
    #   - não é o usuário que está saindo
    #   - não é organizador de outra party ativa
    #   - ordenado pelo mais antigo (created_at ASC)
    # -------------------------------------------------------------------------
    def get_next_eligible_organizer(
        self, party_id: int, exclude_user_id: int
    ) -> Optional[PartyMember]:
        # Subquery: IDs de usuários que já são organizadores de outra party ativa
        active_organizer_ids = (
            self.db.query(Party.organizer_id)
            .filter(
                Party.status.in_([PartyStatus.PENDING, PartyStatus.APPROVED]),
                Party.id != party_id,
            )
            .subquery()
        )

        return (
            self.db.query(PartyMember)
            .filter(
                PartyMember.party_id == party_id,
                PartyMember.user_id != exclude_user_id,
                PartyMember.status == PartyMemberStatus.APPROVED,
                PartyMember.user_id.notin_(active_organizer_ids),
            )
            .order_by(PartyMember.joined_at.asc())
            .first()
        )

    # -------------------------------------------------------------------------
    # RF19 - Busca todas as parties onde o usuário é membro aprovado
    # Usado para verificar conflitos e para sair de parties em lote
    # -------------------------------------------------------------------------
    def get_approved_by_user(self, user_id: int) -> List[PartyMember]:
        return (
            self.db.query(PartyMember)
            .filter(
                PartyMember.user_id == user_id,
                PartyMember.status == PartyMemberStatus.APPROVED,
            )
            .all()
        )

    # -------------------------------------------------------------------------
    # RF18 - Busca membros aprovados de uma party (para remoção pelo organizador)
    # -------------------------------------------------------------------------
    def get_approved_by_party(self, party_id: int) -> List[PartyMember]:
        return (
            self.db.query(PartyMember)
            .filter(
                PartyMember.party_id == party_id,
                PartyMember.status == PartyMemberStatus.APPROVED,
            )
            .all()
        )