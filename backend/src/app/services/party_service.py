from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.app.models.party import Party, PartyStatus
from src.app.models.audit_log import AuditAction
from src.app.models.user import User, UserRole
from src.app.repositories.party_repository import PartyRepository
from src.app.repositories.game_repository import GameRepository
from src.app.repositories.party_member_repository import PartyMemberRepository
from src.app.schemas.party import PartyCreate, PartyUpdate
from src.app.core.aspects import audit_action, log_execution
from src.app.services.audit_service import AuditService
from src.app.internal import publish_event, LudotecaEvent


class PartyService:
    def __init__(self, db: Session):
        self.repo = PartyRepository(db)
        self.game_repo = GameRepository(db)
        self.member_repo = PartyMemberRepository(db)
        self.audit = AuditService(db)

    # -------------------------------------------------------------------------
    # RF08 | RN09 | RN10 | RN11 | RN12 | RN18 | RN19
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY", action="CREATE")
    async def create_party(self, party_in: PartyCreate, current_user: User) -> Party:
        # RN11 - Jogo deve existir e estar disponível
        game = self.game_repo.get_by_id(party_in.game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jogo não encontrado."
            )
        if not game.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jogo indisponível para reserva."
            )

        # RN12 - Deve haver cópias livres do jogo
        active_parties_count = self.repo.count_active_by_game(party_in.game_id)
        if active_parties_count >= game.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não há cópias disponíveis deste jogo no momento."
            )

        # RN09 - Organizador não pode reservar o mesmo jogo mais de uma vez
        existing_same_game = self.repo.get_active_by_organizer_and_game(
            organizer_id=current_user.id,
            game_id=party_in.game_id
        )
        if existing_same_game:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Você já possui uma party ativa com este jogo."
            )

        # RN10 - Organizador não pode ter mais de uma party PENDING ou APPROVED
        existing_active = self.repo.get_active_by_organizer(current_user.id)
        if existing_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Você já possui uma party pendente ou aprovada. Finalize-a antes de criar outra."
            )

        # RN18 - Party nasce com status PENDING (explícito)
        data = party_in.model_dump()
        data["organizer_id"] = current_user.id
        data["status"] = PartyStatus.PENDING

        party = self.repo.create(data)
        await self.audit.log("PARTY", party.id, AuditAction.CREATE, current_user.id)
        await publish_event(
            LudotecaEvent.PARTY_CREATED,
            {"party_id": party.id, "organizer_id": current_user.id}
        )
        return party

    # -------------------------------------------------------------------------
    # RF09 - Listar todas as parties (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_all(self) -> List[Party]:
        return self.repo.get_all()

    # -------------------------------------------------------------------------
    # RF10 - Listar parties abertas (APPROVED) para solicitação de entrada
    # Alias mantido para compatibilidade com o controller (get_open_parties).
    # -------------------------------------------------------------------------
    @log_execution
    async def get_open_parties(self) -> List[Party]:
        return self.repo.get_by_status(PartyStatus.APPROVED)

    # -------------------------------------------------------------------------
    # RF11 - Listar parties disponíveis (APPROVED) para usuário base
    # -------------------------------------------------------------------------
    @log_execution
    async def get_available_parties(self) -> List[Party]:
        return self.repo.get_by_status(PartyStatus.APPROVED)

    # -------------------------------------------------------------------------
    # RF10 - Listar parties do próprio usuário
    # -------------------------------------------------------------------------
    @log_execution
    async def get_my_parties(self, user_id: int) -> List[Party]:
        return self.repo.get_by_member_or_organizer(user_id)

    # -------------------------------------------------------------------------
    # RF29 - Listar parties por status (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_parties_by_status(self, party_status: PartyStatus) -> List[Party]:
        return self.repo.get_by_status(party_status)

    # -------------------------------------------------------------------------
    # RF13 - Ver detalhes de uma party
    # -------------------------------------------------------------------------
    @log_execution
    async def get_by_id(self, party_id: int) -> Party:
        party = self.repo.get_by_id(party_id)
        if not party:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Party não encontrada."
            )
        return party

    # -------------------------------------------------------------------------
    # RF09 | RN21 - Editar party (apenas organizador, apenas PENDING)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY", action="UPDATE")
    async def update_party(
        self,
        party_id: int,
        party_in: PartyUpdate,
        current_user: User
    ) -> Party:
        party = await self.get_by_id(party_id)

        # RN21 - Apenas o organizador pode editar
        if party.organizer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode editar a party."
            )

        # RN21 - Apenas parties PENDING podem ser editadas
        if party.status != PartyStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas parties com status PENDENTE podem ser editadas."
            )

        # RN21 - Apenas campos permitidos
        allowed_fields = {"description", "date", "time", "max_players"}
        update_data = {
            k: v for k, v in party_in.model_dump(exclude_none=True).items()
            if k in allowed_fields
        }

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo válido para atualização foi informado."
            )

        updated = self.repo.update(party, update_data)
        await self.audit.log("PARTY", party_id, AuditAction.UPDATE, current_user.id)
        return updated

    # -------------------------------------------------------------------------
    # RF31 | RN18 | RN19 - Aprovar party (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY", action="APPROVE")
    async def approve_party(self, party_id: int, current_user: User) -> Party:
        party = await self.get_by_id(party_id)

        if party.status != PartyStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas parties com status PENDENTE podem ser aprovadas."
            )

        # Revalida disponibilidade do jogo no momento da aprovação
        game = self.game_repo.get_by_id(party.game_id)
        if not game or not game.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O jogo desta party não está mais disponível."
            )

        # Revalida cópias disponíveis no momento da aprovação
        active_count = self.repo.count_active_by_game(party.game_id)
        if active_count >= game.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não há mais cópias disponíveis deste jogo para aprovação."
            )

        updated = self.repo.update(party, {"status": PartyStatus.APPROVED})
        await self.audit.log("PARTY", party_id, AuditAction.APPROVE, current_user.id)
        await publish_event(LudotecaEvent.PARTY_APPROVED, {"party_id": party_id})
        return updated

    # -------------------------------------------------------------------------
    # RF31 | RN18 | RN19 - Rejeitar party (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY", action="REJECT")
    async def reject_party(self, party_id: int, current_user: User) -> Party:
        party = await self.get_by_id(party_id)

        if party.status != PartyStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas parties com status PENDENTE podem ser rejeitadas."
            )

        updated = self.repo.update(party, {"status": PartyStatus.REJECTED})
        await self.audit.log("PARTY", party_id, AuditAction.REJECT, current_user.id)
        await publish_event(LudotecaEvent.PARTY_REJECTED, {"party_id": party_id})
        return updated

    # -------------------------------------------------------------------------
    # RF14 | RN19 - Cancelar party (organizador ou admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY", action="CANCEL")
    async def cancel_party(self, party_id: int, current_user: User) -> Party:
        party = await self.get_by_id(party_id)

        # Apenas organizador ou admin podem cancelar
        is_organizer = party.organizer_id == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not is_organizer and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador ou um administrador pode cancelar a party."
            )

        if party.status == PartyStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Party já está cancelada."
            )

        updated = self.repo.update(party, {"status": PartyStatus.CANCELLED})
        await self.audit.log("PARTY", party_id, AuditAction.CANCEL, current_user.id)
        await publish_event(LudotecaEvent.PARTY_CANCELLED, {"party_id": party_id})
        return updated

    # -------------------------------------------------------------------------
    # RF32 | RN19 - Excluir party rejeitada manualmente (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="PARTY", action="DELETE")
    async def delete_rejected_party(self, party_id: int, current_user: User) -> bool:
        party = await self.get_by_id(party_id)

        if party.status != PartyStatus.REJECTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas parties REJEITADAS podem ser excluídas manualmente."
            )

        await self.audit.log("PARTY", party_id, AuditAction.DELETE, current_user.id)
        self.repo.delete(party_id)
        return True

    # -------------------------------------------------------------------------
    # RF33 | RN20 - Excluir parties rejeitadas há mais de 90 dias (Sistema)
    # -------------------------------------------------------------------------
    @log_execution
    async def delete_old_rejected_parties(self) -> int:
        limit_date = datetime.utcnow() - timedelta(days=90)
        old_parties = self.repo.get_old_rejected_parties(limit_date)

        deleted_count = 0
        for party in old_parties:
            await self.audit.log("PARTY", party.id, AuditAction.DELETE, None)
            self.repo.delete(party.id)
            deleted_count += 1

        return deleted_count

    # -------------------------------------------------------------------------
    # RN06 - Cancelar parties quando jogo é deletado
    # -------------------------------------------------------------------------
    @log_execution
    async def cancel_parties_by_deleted_game(self, game_id: int) -> int:
        active_parties = self.repo.get_active_by_game(game_id)

        cancelled_count = 0
        for party in active_parties:
            self.repo.update(party, {"status": PartyStatus.CANCELLED})
            await self.audit.log("PARTY", party.id, AuditAction.CANCEL, None)
            await publish_event(
                LudotecaEvent.PARTY_CANCELLED,
                {"party_id": party.id, "reason": "game_deleted"}
            )
            cancelled_count += 1

        return cancelled_count

    # -------------------------------------------------------------------------
    # RN07 - Cancelar parties quando jogo é indisponibilizado
    # -------------------------------------------------------------------------
    @log_execution
    async def cancel_parties_by_unavailable_game(self, game_id: int) -> int:
        active_parties = self.repo.get_active_by_game(game_id)

        cancelled_count = 0
        for party in active_parties:
            self.repo.update(party, {"status": PartyStatus.CANCELLED})
            await self.audit.log("PARTY", party.id, AuditAction.CANCEL, None)
            await publish_event(
                LudotecaEvent.PARTY_CANCELLED,
                {"party_id": party.id, "reason": "game_unavailable"}
            )
            cancelled_count += 1

        return cancelled_count

    # -------------------------------------------------------------------------
    # RN08 - Transferir organizador ou deletar party
    # Chamado por: UserService ao inativar/deletar usuário, ou ao sair da party
    # -------------------------------------------------------------------------
    @log_execution
    async def transfer_or_delete_party(
        self,
        party_id: int,
        leaving_user_id: int
    ) -> Optional[Party]:
        party = await self.get_by_id(party_id)

        # Busca o próximo membro elegível para ser organizador:
        # - aprovado na party
        # - não é organizador de outra party ativa
        next_organizer = self.member_repo.get_next_eligible_organizer(
            party_id=party_id,
            exclude_user_id=leaving_user_id
        )

        if next_organizer:
            updated = self.repo.update(party, {"organizer_id": next_organizer.user_id})
            await self.audit.log("PARTY", party_id, AuditAction.UPDATE, leaving_user_id)
            return updated
        else:
            # Nenhum membro elegível → party é deletada
            await self.audit.log("PARTY", party_id, AuditAction.DELETE, leaving_user_id)
            self.repo.delete(party_id)
            return None