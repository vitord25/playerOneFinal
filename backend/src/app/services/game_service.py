from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.app.models.game import Game
from src.app.models.audit_log import AuditAction
from src.app.models.user import User, UserRole
from src.app.repositories.game_repository import GameRepository
from src.app.schemas.game import GameCreate, GameUpdate
from src.app.core.aspects import audit_action, log_execution
from src.app.services.audit_service import AuditService
from src.app.internal import publish_event, LudotecaEvent


class GameService:
    def __init__(self, db: Session):
        self.repo = GameRepository(db)
        self.audit = AuditService(db)

    # -------------------------------------------------------------------------
    # RF01 | RN01 | RN02 | RN19 - Criar jogo (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="GAME", action="CREATE")
    async def create_game(self, game_in: GameCreate, current_user: User) -> Game:
        data = game_in.model_dump()

        # RN01 - max_players >= min_players
        if data["max_players"] < data["min_players"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_players deve ser maior ou igual a min_players."
            )

        # RN02 - max_duration >= min_duration
        if data["max_duration_minutes"] < data["min_duration_minutes"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_duration_minutes deve ser maior ou igual a min_duration_minutes."
            )

        game = self.repo.create(data)
        await self.audit.log("GAME", game.id, AuditAction.CREATE, current_user.id)
        return game

    # -------------------------------------------------------------------------
    # RF03 - Listar todos os jogos (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_all(self) -> List[Game]:
        return self.repo.get_all()

    # -------------------------------------------------------------------------
    # RF02 - Listar jogos disponíveis (Base User)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_available(self) -> List[Game]:
        return self.repo.get_available_games()

    # -------------------------------------------------------------------------
    # RF04 - Buscar jogo por ID
    # -------------------------------------------------------------------------
    @log_execution
    async def get_by_id(self, game_id: int) -> Game:
        game = self.repo.get_by_id(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jogo não encontrado."
            )
        return game

    # -------------------------------------------------------------------------
    # RF05 | RN01 | RN02 | RN19 - Atualizar jogo (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="GAME", action="UPDATE")
    async def update_game(
        self, game_id: int, game_in: GameUpdate, current_user: User
    ) -> Game:
        game = await self.get_by_id(game_id)
        update_data = game_in.model_dump(exclude_none=True)

        # RN01 - Revalida min/max players se algum dos dois for alterado
        new_min = update_data.get("min_players", game.min_players)
        new_max = update_data.get("max_players", game.max_players)
        if new_max < new_min:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_players deve ser maior ou igual a min_players."
            )

        # RN02 - Revalida min/max duration se algum dos dois for alterado
        new_min_dur = update_data.get("min_duration_minutes", game.min_duration_minutes)
        new_max_dur = update_data.get("max_duration_minutes", game.max_duration_minutes)
        if new_max_dur < new_min_dur:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_duration_minutes deve ser maior ou igual a min_duration_minutes."
            )

        updated = self.repo.update(game, update_data)
        await self.audit.log("GAME", game_id, AuditAction.UPDATE, current_user.id)
        return updated

    # -------------------------------------------------------------------------
    # RF06 | RN06 | RN19 - Deletar jogo (Admin)
    # Cancela parties ativas antes de deletar
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="GAME", action="DELETE")
    async def delete_game(self, game_id: int, current_user: User) -> bool:
        await self.get_by_id(game_id)

        # RN06 - Cancela parties ativas antes de deletar o jogo
        await self._cancel_active_parties(
            game_id=game_id,
            reason="game_deleted",
            actor_id=current_user.id,
        )

        await self.audit.log("GAME", game_id, AuditAction.DELETE, current_user.id)
        self.repo.delete(game_id)
        return True

    # -------------------------------------------------------------------------
    # RF07 | RN07 | RN19 - Bloquear / desbloquear jogo (Admin)
    # Ao bloquear: cancela parties ativas
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="GAME", action="UPDATE")
    async def toggle_availability(
        self, game_id: int, current_user: User
    ) -> Game:
        game = await self.get_by_id(game_id)
        new_availability = not game.available

        # RN07 - Se estiver desativando, cancela parties ativas
        if not new_availability:
            await self._cancel_active_parties(
                game_id=game_id,
                reason="game_unavailable",
                actor_id=current_user.id,
            )

        updated = self.repo.update(game, {"available": new_availability})
        await self.audit.log("GAME", game_id, AuditAction.UPDATE, current_user.id)
        await publish_event(
            LudotecaEvent.GAME_AVAILABILITY_CHANGED,
            {"game_id": game_id, "available": new_availability}
        )
        return updated

    # -------------------------------------------------------------------------
    # Método interno - cancela parties ativas de um jogo
    # Usado por delete_game e toggle_availability
    # -------------------------------------------------------------------------
    async def _cancel_active_parties(
        self, game_id: int, reason: str, actor_id: int
    ) -> None:
        from src.app.services.party_service import PartyService
        party_service = PartyService(self.repo.db)

        if reason == "game_deleted":
            await party_service.cancel_parties_by_deleted_game(game_id)
        else:
            await party_service.cancel_parties_by_unavailable_game(game_id)