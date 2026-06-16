from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.app.core.database import get_db
from src.app.core.security import get_current_user, require_role
from src.app.models.user import User, UserRole
from src.app.schemas.game import GameCreate, GameUpdate, GameResponse
from src.app.internal.factory import get_factory

router = APIRouter()


# ─────────────────────────────────────────────
# POST /games — RF01 | Admin
# ─────────────────────────────────────────────
@router.post(
    "/",
    response_model=GameResponse,
    status_code=201,
    summary="Cadastrar novo jogo (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def create_game(
    game_in: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).game_service().create_game(game_in, current_user)


# ─────────────────────────────────────────────
# GET /games — RF03 | Admin
# ─────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[GameResponse],
    summary="Listar todos os jogos (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def list_all_games(
    db: Session = Depends(get_db),
):
    return await get_factory(db).game_service().get_all()


# ─────────────────────────────────────────────
# GET /games/available — RF02 | Autenticado
# ─────────────────────────────────────────────
@router.get(
    "/available",
    response_model=List[GameResponse],
    summary="Listar jogos disponíveis",
)
async def list_available_games(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await get_factory(db).game_service().get_available()


# ─────────────────────────────────────────────
# GET /games/{game_id} — RF04 | Autenticado
# ─────────────────────────────────────────────
@router.get(
    "/{game_id}",
    response_model=GameResponse,
    summary="Buscar jogo por ID",
)
async def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await get_factory(db).game_service().get_by_id(game_id)


# ─────────────────────────────────────────────
# PATCH /games/{game_id} — RF05 | Admin
# ─────────────────────────────────────────────
@router.patch(
    "/{game_id}",
    response_model=GameResponse,
    summary="Atualizar dados do jogo (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def update_game(
    game_id: int,
    game_in: GameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).game_service().update_game(game_id, game_in, current_user)


# ─────────────────────────────────────────────
# PATCH /games/{game_id}/availability — RF07 | Admin
# ─────────────────────────────────────────────
@router.patch(
    "/{game_id}/availability",
    response_model=GameResponse,
    summary="Bloquear / desbloquear jogo (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def toggle_availability(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await get_factory(db).game_service().toggle_availability(game_id, current_user)


# ─────────────────────────────────────────────
# DELETE /games/{game_id} — RF06 | Admin
# ─────────────────────────────────────────────
@router.delete(
    "/{game_id}",
    status_code=204,
    summary="Deletar jogo (Admin)",
    dependencies=[Depends(require_role([UserRole.ADMIN]))],
)
async def delete_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await get_factory(db).game_service().delete_game(game_id, current_user)