import logging
from typing import List, Type
import random
from datetime import datetime
from avalon.player.base import BasePlayer
from avalon.player.baseline import NaivePlayer, RandomPlayer
from avalon.logger import GameLogger


class Game:
    def __init__(self, player_classes: List[Type[BasePlayer]]):
        self.logger = GameLogger()
        self.num_players = 7
        self.players = self.create_players(player_classes)
        self.quests = []
        self.current_quest = 0
        self.evil_players = []
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
            if not player.is_loyal:
                self.evil_players.append(player)
            self.logger.log_admin(f"Assigned role {roles[i]} to {player}")

    def reveal_evil_players(self):
        self.logger.log_public('All players close their eyes. Evil players open their eyes and identify their teammates.')
        for player in self.evil_players:
            player.known_evil_players = self.evil_players
        self.logger.log_evil(f'The evil players are: {[str(player) for player in self.evil_players]}')

    def assign_first_leader(self) -> int:
        leader_index = random.randint(0, len(self.players) - 1)
        self.logger.log_public(f"Assigned first leader {self.players[leader_index]}")
        return leader_index

    def select_quest_team(self) -> List[BasePlayer]:
        return random.sample(self.players, 3)

    def vote_on_team(self, team: List[BasePlayer]) -> bool:
        votes = [player.vote_on_team(team) for player in self.players]
        result = votes.count(True) > votes.count(False)
        self.logger.log_public(f"Team {self.rejected_teams+1} vote result: {'Approved' if result else 'Rejected'}")
        return result

    def conduct_quest(self, team: List[BasePlayer]) -> bool:
        votes = [player.conduct_quest(team) for player in team]
        n_fails = votes.count(False)
        result = n_fails < self.current_quest_fails_required
        self.logger.log_public(f'Quest votes: {votes}')
        self.logger.log_public(f"Quest {self.current_quest+1} result: {'Success' if result else 'Failure'}")
        return result

    def play_game(self) -> str:
        self.assign_roles()
        self.reveal_evil_players()
        leader_index = self.assign_first_leader()
        self.rejected_teams = 0

        for quest in range(5):
            self.logger.log_public(f"Starting quest {quest+1}")
            self.current_quest = quest
            self.current_quest_fails_required = self.fails_required[quest]
            num_players = self.players_per_quest[quest]
            is_team_accepted = False

            while not is_team_accepted:
                self.logger.log_public(f'Proposing team {self.rejected_teams+1}')
                proposer = self.players[leader_index]
                team = proposer.propose_team(num_players)
                self.logger.log_public(f"{proposer} proposed team: {[str(player) for player in team]}")
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
                        self.logger.log_public("Five teams rejected in a row. Evil team wins.")
                        return "Minions"
                leader_index = (leader_index + 1) % len(self.players)
            self.logger.log_public(f'Quests results: {self.quests}')
            if self.quests.count(True) >= 3:
                self.logger.log_public("Loyal team wins.")
                return "Loyal Servants"
            elif self.quests.count(False) >= 3:
                self.logger.log_public("Evil team wins.")
                return "Minions"

def play():
    player_classes = [NaivePlayer] * 7
    game = Game(player_classes)
    game.play_game()

if __name__ == "__main__":
    play()