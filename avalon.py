import logging
from typing import List, Dict, Type, TypeVar
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
                    level=logging.DEBUG,
                    # filename=f'logs/avalon_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

PlayerType = TypeVar('PlayerType', bound='BasePlayer')

class BasePlayer:
    def __init__(self, name: str, game: 'Game'):
        self.name = name
        self.game = game

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
        logging.info(f"{self} proposed team: {[str(player) for player in team]}")
        return team
        
    def vote_on_team(self, team: List[PlayerType]) -> bool:
        vote = random.choice([True, False])
        logging.info(f"{self} voted {'Yes' if vote else 'No'}")
        return vote
    
    def conduct_quest(self, team: List[PlayerType]) -> bool:
        success = random.choice([True, False])
        logging.info(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success


class NaivePlayer(BasePlayer):
    def propose_team(self, num_players: int) -> List[PlayerType]:
        # Includes self in the team
        available_players = [player for player in self.game.players if player != self]
        team = [self] + random.sample(available_players, num_players - 1)
        logging.info(f"{self} proposed team: {[str(player) for player in team]}")
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
        logging.info(f"{self} voted {'Yes' if vote else 'No'}")
        return vote

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        # Always succeeds if is loyal, otherwise fails randomly
        if self.is_loyal:
            success = True
        else:
            success = random.choice([True, False])
        logging.info(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success


class Game:
    def __init__(self, player_classes: List[Type[BasePlayer]]):
        self.num_players = 7
        self.players = self.create_players(player_classes)
        self.quests = []
        self.current_quest = 0
        self.players_per_quest = [2, 3, 3, 4, 4]
        self.fails_required = [1, 1, 1, 2, 1]

    def create_players(self, player_classes: List[Type[BasePlayer]]) -> List[BasePlayer]:
        players = []
        for i, player_class in enumerate(player_classes):
            players.append(player_class(f"Player {i+1}", self))
        return players

    def assign_roles(self):
        roles = ['Loyal Servant'] * 4 + ['Minion'] * 3
        random.shuffle(roles)
        for i, player in enumerate(self.players):
            player.assign_role(roles[i])
            logging.info(f"Assigned role {roles[i]} to {player}")

    def assign_first_leader(self) -> int:
        leader_index = random.randint(0, len(self.players) - 1)
        logging.info(f"Assigned first leader {self.players[leader_index]}")
        return leader_index

    def select_quest_team(self) -> List[BasePlayer]:
        return random.sample(self.players, 3)

    def vote_on_team(self, team: List[BasePlayer]) -> bool:
        votes = [player.vote_on_team(team) for player in self.players]
        result = votes.count(True) > votes.count(False)
        logging.info(f"Team {self.rejected_teams+1} vote result: {'Approved' if result else 'Rejected'}")
        return result

    def conduct_quest(self, team: List[BasePlayer]) -> bool:
        votes = [player.conduct_quest(team) for player in team]
        n_fails = votes.count(False)
        result = n_fails < self.current_quest_fails_required
        logging.info(f'Quest votes: {votes}')
        logging.info(f"Quest {self.current_quest+1} result: {'Success' if result else 'Failure'}")
        return result

    def play_game(self) -> str:
        self.assign_roles()
        leader_index = self.assign_first_leader()
        self.rejected_teams = 0

        for quest in range(5):
            logging.info(f"Starting quest {quest+1}")
            self.current_quest = quest
            self.current_quest_fails_required = self.fails_required[quest]
            num_players = self.players_per_quest[quest]
            is_team_accepted = False

            while not is_team_accepted:
                logging.info(f'Proposing team {self.rejected_teams+1}')
                proposer = self.players[leader_index]
                team = proposer.propose_team(num_players)
                if self.vote_on_team(team):
                    if self.conduct_quest(team):
                        self.quests.append(True)
                    else:
                        self.quests.append(False)
                    self.rejected_teams = 0
                    is_team_accepted = True
                else:
                    self.rejected_teams += 1
                    if self.rejected_teams >= 5:
                        logging.info("Five teams rejected in a row. Evil team wins.")
                        return "Minions"
                leader_index = (leader_index + 1) % len(self.players)
            logging.info(f'Quests: {self.quests}')
            if self.quests.count(True) >= 3:
                logging.info("Loyal team wins.")
                return "Loyal Servants"
            elif self.quests.count(False) >= 3:
                logging.info("Evil team wins.")
                return "Minions"


if __name__ == "__main__":
    player_classes = [NaivePlayer] * 7
    game = Game(player_classes)
    game.play_game()