import random
import logging
from typing import List, TypeVar

PlayerType = TypeVar('PlayerType', bound='BasePlayer')

class BasePlayer:
    def __init__(self, name: str, game: 'Game'):
        self.name = name
        self.game = game
        self.logger = game.logger
        self.known_evil_players = []

    def __str__(self):
        return f'{self.__class__.__name__} {self.name} ({"Loyal" if self.is_loyal else "Evil"})'

    def assign_role(self, role: str):
        self.role = role
        self.is_loyal = role in ["Merlin", "Loyal Servant"]

    def propose_team(self) -> List[PlayerType]:
        raise NotImplementedError

    def vote_on_team(self, team: List[PlayerType]) -> bool:
        raise NotImplementedError

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        raise NotImplementedError

class RandomPlayer(BasePlayer):
    def propose_team(self, num_players: int) -> List[PlayerType]:
        team = random.sample(self.game.players, num_players)
        self.logger.log(f"{self} proposed team: {[str(player) for player in team]}")
        return team
        
    def vote_on_team(self, team: List[PlayerType]) -> bool:
        vote = random.choice([True, False])
        self.logger.log(f"{self} voted {'Yes' if vote else 'No'}")
        return vote
    
    def conduct_quest(self, team: List[PlayerType]) -> bool:
        success = random.choice([True, False])
        self.logger.log(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success


class NaivePlayer(BasePlayer):
    def propose_team(self, num_players: int) -> List[PlayerType]:
        # Includes self in the team
        available_players = [player for player in self.game.players if player != self]
        team = [self] + random.sample(available_players, num_players - 1)
        self.logger.log(f"{self} proposed team: {[str(player) for player in team]}")
        return team

    def vote_on_team(self, team: List[PlayerType]) -> bool:
        # Loyal players vote yes if they are in the team, otherwise random
        if self.is_loyal:
            if self in team:
                vote = True
            else:
                vote = random.choice([True, False])
        # Evil players vote yes to teams with enough evil players to fail the quest
        else:
            n_evil_players = sum([1 for player in team if not player.is_loyal])
            if n_evil_players >= self.game.current_quest_fails_required:
                vote = True
            else:
                vote = False
        self.logger.log(f"{self} voted {'Yes' if vote else 'No'}")
        return vote

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        # Always succeeds if is loyal, otherwise fails randomly
        if self.is_loyal:
            success = True
        else:
            success = random.choice([True, False])
        self.logger.log(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success

