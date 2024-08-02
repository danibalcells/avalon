from typing import List, Type
import random
from datetime import datetime

import fantasynames

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
        self.rejected_teams = 0
        self.evil_players = []
        self.players_per_quest = [2, 3, 3, 4, 4]
        self.fails_required = [1, 1, 1, 2, 1]

    def create_players(self, player_classes: List[Type[BasePlayer]]) -> List[BasePlayer]:
        players = {}
        for i, player_class in enumerate(player_classes):
            player_name = fantasynames.human()
            players[i] = player_class(player_name, i, self)
            self.logger.log_public(f'"{player_name}" joins the game.')
        return players

    def format_player_list(self, players: List[BasePlayer] = None) -> str:
        if players is None:
            players = self.list_players()
        return '\n'.join([f'{i}: {player}' for i, player in enumerate(players)])

    def list_players(self) -> List[BasePlayer]:
        return list(self.players.values())

    def get_players_by_ids(self, ids: List[int]) -> List[BasePlayer]:
        return [self.players[i] for i in ids]

    def assign_roles(self):
        roles = ['Loyal Servant'] * 4 + ['Minion'] * 3
        random.shuffle(roles)
        self.logger.log_public('Role cards are shuffled and dealt to players. Players look at their card privately.')
        self.evil_players = []
        for i, player in enumerate(self.list_players()):
            player.assign_role(roles[i])
            if not player.is_loyal:
                self.evil_players.append(player)
            self.logger.log_admin(f"Assigned role {roles[i]} to {player}")

    def reveal_evil_players(self):
        self.logger.log_public('All players close their eyes. Evil players open their eyes and identify their teammates. Evil players close their eyes. All players open their eyes and the game begins.')
        for player in self.evil_players:
            player.known_evil_players = self.evil_players
        self.logger.log_evil(f'The evil players are: {[f"{player.id}: {player}" for player in self.evil_players]}')

    def assign_first_leader(self) -> int:
        leader_index = random.randint(0, len(self.list_players()) - 1)
        self.logger.log_public(f"Assigned first leader {self.list_players()[leader_index]}")
        return leader_index

    def select_quest_team(self) -> List[BasePlayer]:
        return random.sample(self.list_players(), 3)

    def vote_on_team(self, team: List[BasePlayer]) -> bool:
        votes = [player.vote_on_team(team) for player in self.list_players()]
        result = votes.count(True) > votes.count(False)
        self.logger.log_public(f"Team {self.rejected_teams+1} vote result: {'Approved' if result else 'Rejected'}")
        for player in self.list_players():
            if player.is_bot:
                self.logger.log_public(f'{player.name} explanation: {player.last_vote_explanation}')
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
                self.logger.log_public(f'It is {proposer}\'s turn to propose a team.')
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