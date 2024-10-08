from typing import List, TypeVar

PlayerType = TypeVar('PlayerType', bound='BasePlayer')

class BasePlayer:
    def __init__(self, name: str, player_id: int, game: 'Game'):
        self.id = player_id
        self.name = name
        self.game = game
        self.logger = game.logger
        self.known_evil_players = []

    def __str__(self):
        return self.name

    def assign_role(self, role: str):
        self.role = role
        self.is_loyal = role in ["Merlin", "Loyal Servant"]
        self.is_evil = not self.is_loyal
        self.allegiance = 'Loyal' if self.is_loyal else 'Evil'

    def propose_team(self) -> List[PlayerType]:
        raise NotImplementedError

    def vote_on_team(self, team: List[PlayerType]) -> bool:
        raise NotImplementedError

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        raise NotImplementedError
