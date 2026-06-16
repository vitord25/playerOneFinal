from typing import List
from sqlalchemy.orm import Session

from src.app.models.game import Game
from src.app.repositories.base_repository import BaseRepository


class GameRepository(BaseRepository[Game]):
    def __init__(self, db: Session):
        super().__init__(Game, db)

    # RF02 - Jogos disponíveis para usuário base
    def get_available_games(self) -> List[Game]:
        return (
            self.db.query(Game)
            .filter(Game.available == True)
            .all()
        )

    # RF03 - Todos os jogos para admin (incluindo indisponíveis)
    def get_all_games(self) -> List[Game]:
        return self.db.query(Game).all()

    # Busca por nome (útil para filtros futuros)
    def get_by_name(self, name: str) -> Game:
        return (
            self.db.query(Game)
            .filter(Game.name == name)
            .first()
        )