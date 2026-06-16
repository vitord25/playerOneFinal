from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.app.models.message import Message
from src.app.models.party import PartyStatus
from src.app.models.party_member import PartyMemberStatus
from src.app.models.audit_log import AuditAction
from src.app.models.user import User, UserRole
from src.app.repositories.message_repository import MessageRepository
from src.app.repositories.party_member_repository import PartyMemberRepository
from src.app.repositories.party_repository import PartyRepository
from src.app.schemas.message import MessageCreate
from src.app.core.aspects import audit_action, log_execution
from src.app.services.audit_service import AuditService
from src.app.internal import publish_event, LudotecaEvent


class MessageService:
    def __init__(self, db: Session):
        self.repo = MessageRepository(db)
        self.member_repo = PartyMemberRepository(db)
        self.party_repo = PartyRepository(db)
        self.audit = AuditService(db)

    # -------------------------------------------------------------------------
    # RF20 | RN22 | RN19 - Enviar mensagem
    # Quem pode enviar: membros aprovados + organizador da party
    # Party deve estar APPROVED
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="MESSAGE", action="CREATE")
    async def send_message(
        self,
        party_id: int,
        message_in: MessageCreate,
        current_user: User,
    ) -> Message:
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )

        # RN22 - Party deve estar APPROVED para aceitar mensagens
        if party.status != PartyStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mensagens só podem ser enviadas em parties aprovadas."
            )

        # Organizador pode enviar sem ser membro formal
        is_organizer = party.organizer_id == current_user.id

        if not is_organizer:
            membership = self.member_repo.get_by_user_and_party(current_user.id, party_id)
            if not membership or membership.status != PartyMemberStatus.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Apenas membros aprovados podem enviar mensagens."
                )

        message = self.repo.create({
            "user_id": current_user.id,
            "party_id": party_id,
            "content": message_in.content,
        })
        await self.audit.log("MESSAGE", message.id, AuditAction.CREATE, current_user.id)
        await publish_event(
            LudotecaEvent.MESSAGE_SENT,
            {"party_id": party_id, "user_id": current_user.id, "message_id": message.id}
        )
        return message

    # -------------------------------------------------------------------------
    # RF21 | RN22 - Listar mensagens de uma party
    # Quem pode ver: membros aprovados + organizador + admin
    # Ordenação: crescente por created_at (mais antigas primeiro)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_by_party(
        self,
        party_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )

        # Admin pode ver qualquer party
        if current_user.role == UserRole.ADMIN:
            return self.repo.get_by_party(party_id, skip=skip, limit=limit)

        # Organizador pode ver sem ser membro formal
        if party.organizer_id == current_user.id:
            return self.repo.get_by_party(party_id, skip=skip, limit=limit)

        # Usuário base: precisa ser membro aprovado
        membership = self.member_repo.get_by_user_and_party(current_user.id, party_id)
        if not membership or membership.status != PartyMemberStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas membros aprovados podem visualizar mensagens."
            )

        return self.repo.get_by_party(party_id, skip=skip, limit=limit)

    # -------------------------------------------------------------------------
    # RF22 | RN19 - Deletar mensagem (Admin)
    # Moderação: admin pode remover qualquer mensagem
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="MESSAGE", action="DELETE")
    async def delete_message(
        self, message_id: int, current_user: User
    ) -> bool:
        message = self.repo.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensagem não encontrada."
            )

        await self.audit.log("MESSAGE", message_id, AuditAction.DELETE, current_user.id)
        self.repo.delete(message_id)
        return True