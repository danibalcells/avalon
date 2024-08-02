import random
from typing import List, TypeVar
from avalon.player.base import BasePlayer

PlayerType = TypeVar('PlayerType', bound='BasePlayer')

class RandomPlayer(BasePlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_bot = False
        
    def propose_team(self, num_players: int) -> List[PlayerType]:
        team = random.sample(self.game.list_players(), num_players)
        self.logger.log_admin(f"{self} proposed team: {[str(player) for player in team]}")
        return team
        
    def vote_on_team(self, team: List[PlayerType]) -> bool:
        vote = random.choice([True, False])
        self.logger.log_admin(f"{self} voted {'Yes' if vote else 'No'}")
        return vote
    
    def conduct_quest(self, team: List[PlayerType]) -> bool:
        success = random.choice([True, False])
        self.logger.log_admin(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success


class NaivePlayer(BasePlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_bot = False
        
    def propose_team(self, num_players: int) -> List[PlayerType]:
        # Includes self in the team
        available_players = [player for player in self.game.list_players() if player != self]
        team = [self] + random.sample(available_players, num_players - 1)
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
        self.logger.log_admin(f"{self} voted {'Yes' if vote else 'No'}")
        return vote

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        # Always succeeds if is loyal, otherwise fails randomly
        if self.is_loyal:
            success = True
        else:
            success = random.choice([True, False])
        self.logger.log_admin(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success

