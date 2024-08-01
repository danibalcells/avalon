import logging
from typing import List, Type
import random
from datetime import datetime
from .player.base import BasePlayer, NaivePlayer, RandomPlayer

# Configure logging
logging.basicConfig(
                    level=logging.DEBUG,
                    # filename=f'logs/avalon_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')


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

def play():
    player_classes = [NaivePlayer] * 7
    game = Game(player_classes)
    game.play_game()

if __name__ == "__main__":
    play()