from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.app.models.party_member import PartyMember, PartyMemberStatus
from src.app.models.party import PartyStatus
from src.app.models.audit_log import AuditAction
from src.app.models.user import User, UserRole
from src.app.repositories.party_member_repository import PartyMemberRepository
from src.app.repositories.party_repository import PartyRepository
from src.app.core.aspects import audit_action, log_execution
from src.app.services.audit_service import AuditService
from src.app.internal import publish_event, LudotecaEvent


class PartyMemberService:
    def __init__(self, db: Session):
        self.repo = PartyMemberRepository(db)
        self.party_repo = PartyRepository(db)
        self.audit = AuditService(db)

    # -------------------------------------------------------------------------
    # RF15 | RN13 | RN14 | RN15 | RN16 | RN19 - Solicitar entrada na party
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY_MEMBER", action="CREATE")
    async def request_join(self, party_id: int, current_user: User) -> PartyMember:
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )

        # RN15 - Apenas parties APPROVED aceitam solicitações
        if party.status != PartyStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas parties aprovadas aceitam solicitações de participação."
            )

        # Organizador não pode solicitar entrada na própria party
        if party.organizer_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O organizador não pode solicitar entrada na própria party."
            )

        # RN17 - Solicitação única por party
        if self.repo.get_by_user_and_party(current_user.id, party_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Você já possui uma solicitação para esta party."
            )

        # RN16 - Lotação máxima
        approved_count = self.repo.get_approved_members_count(party_id)
        if approved_count >= party.max_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Party já atingiu o número máximo de jogadores."
            )

        # RN13 / RN14 - Conflito de horário
        conflicting = self.repo.get_approved_conflicting(
            user_id=current_user.id,
            party_date=party.date,
            party_time=party.time,
        )
        if conflicting:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Você já está aprovado em outra party no mesmo horário."
            )

        member = self.repo.create({
            "user_id": current_user.id,
            "party_id": party_id,
            "status": PartyMemberStatus.PENDING,
        })
        await self.audit.log("PARTY_MEMBER", member.id, AuditAction.CREATE, current_user.id)
        await publish_event(
            LudotecaEvent.MEMBER_REQUESTED,
            {"party_id": party_id, "user_id": current_user.id}
        )
        return member

    # -------------------------------------------------------------------------
    # RF16 | RN16 | RN19 - Aprovar membro (apenas organizador da party)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY_MEMBER", action="APPROVE")
    async def approve_member(
        self, member_id: int, current_user: User
    ) -> PartyMember:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitação não encontrada."
            )

        party = self.party_repo.get_by_id(member.party_id)

        # Apenas o organizador pode aprovar
        if party.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode aprovar membros."
            )

        # Apenas solicitações PENDING podem ser aprovadas
        if member.status != PartyMemberStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas solicitações pendentes podem ser aprovadas."
            )

        # RN16 - Revalida lotação no momento da aprovação
        approved_count = self.repo.get_approved_members_count(member.party_id)
        if approved_count >= party.max_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Party já atingiu o número máximo de jogadores."
            )

        # RN13 / RN14 - Revalida conflito de horário no momento da aprovação
        conflicting = self.repo.get_approved_conflicting(
            user_id=member.user_id,
            party_date=party.date,
            party_time=party.time,
        )
        if conflicting:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="O usuário já está aprovado em outra party no mesmo horário."
            )

        updated = self.repo.update(member, {
            "status": PartyMemberStatus.APPROVED,
            "approved_by": current_user.id,
            "approved_at": datetime.utcnow(),
        })
        await self.audit.log("PARTY_MEMBER", member_id, AuditAction.APPROVE, current_user.id)
        await publish_event(
            LudotecaEvent.MEMBER_APPROVED,
            {"member_id": member_id, "approver_id": current_user.id}
        )
        return updated

    # -------------------------------------------------------------------------
    # RF17 | RN19 - Rejeitar membro (apenas organizador da party)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY_MEMBER", action="REJECT")
    async def reject_member(
        self, member_id: int, current_user: User
    ) -> PartyMember:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitação não encontrada."
            )

        party = self.party_repo.get_by_id(member.party_id)

        # Apenas o organizador pode rejeitar
        if party.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode rejeitar membros."
            )

        # Apenas solicitações PENDING podem ser rejeitadas
        if member.status != PartyMemberStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas solicitações pendentes podem ser rejeitadas."
            )

        updated = self.repo.update(member, {
            "status": PartyMemberStatus.REJECTED,
            "approved_by": current_user.id,
        })
        await self.audit.log("PARTY_MEMBER", member_id, AuditAction.REJECT, current_user.id)
        await publish_event(
            LudotecaEvent.MEMBER_REJECTED,
            {"member_id": member_id, "approver_id": current_user.id}
        )
        return updated

    # -------------------------------------------------------------------------
    # RF18 | RN19 - Remover membro aprovado (apenas organizador)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY_MEMBER", action="DELETE")
    async def remove_member(
        self, member_id: int, current_user: User
    ) -> bool:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membro não encontrado."
            )

        party = self.party_repo.get_by_id(member.party_id)

        # Apenas o organizador pode remover membros
        if party.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode remover membros da party."
            )

        # Não pode remover a si mesmo via este endpoint (use leave_party)
        if member.user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O organizador não pode remover a si mesmo. Use o endpoint de saída."
            )

        await self.audit.log("PARTY_MEMBER", member_id, AuditAction.DELETE, current_user.id)
        self.repo.delete(member_id)
        await publish_event(
            LudotecaEvent.MEMBER_REMOVED,
            {"member_id": member_id, "removed_by": current_user.id}
        )
        return True

    # -------------------------------------------------------------------------
    # RF19 | RN08 | RN19 - Sair da party (usuário base ou organizador)
    # Se for o organizador → delega transferência ao PartyService
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY_MEMBER", action="DELETE")
    async def leave_party(self, party_id: int, current_user: User) -> bool:
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )

        # Party deve estar APPROVED para sair
        if party.status != PartyStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Só é possível sair de parties aprovadas."
            )

        # RN08 - Se for o organizador, delega ao PartyService
        if party.organizer_id == current_user.id:
            from src.app.services.party_service import PartyService
            party_service = PartyService(self.party_repo.db)
            await party_service.transfer_or_delete_party(
                party_id=party_id,
                leaving_user_id=current_user.id,
            )
            await self.audit.log("PARTY_MEMBER", party_id, AuditAction.DELETE, current_user.id)
            return True

        # Usuário base: verifica se é membro aprovado
        member = self.repo.get_by_user_and_party(current_user.id, party_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Você não é membro desta party."
            )

        if member.status != PartyMemberStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas membros aprovados podem sair da party."
            )

        await self.audit.log("PARTY_MEMBER", member.id, AuditAction.DELETE, current_user.id)
        self.repo.delete(member.id)
        await publish_event(
            LudotecaEvent.MEMBER_LEFT,
            {"party_id": party_id, "user_id": current_user.id}
        )
        return True

    # -------------------------------------------------------------------------
    # RF16 - Listar solicitações pendentes de uma party (organizador)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_pending_by_party(
        self, party_id: int, current_user: User
    ) -> List[PartyMember]:
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )

        if party.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode ver as solicitações pendentes."
            )

        return self.repo.get_pending_by_party(party_id)

    # -------------------------------------------------------------------------
    # RF13 - Listar todos os membros de uma party
    # -------------------------------------------------------------------------
    @log_execution
    async def get_by_party(self, party_id: int) -> List[PartyMember]:
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )
        return self.repo.get_by_party(party_id)