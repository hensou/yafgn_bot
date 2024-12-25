# platforms/base.py
from abc import ABC, abstractmethod
from typing import List
from models import Game

class GamePlatform(ABC):
    @abstractmethod
    async def get_free_games(self) -> List[Game]:
        """Fetch and return a list of currently free games."""
        pass

