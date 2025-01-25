from typing import List
from avalon.player.base import BasePlayer


class TheoryOfMind:
    def __init__(self, players: List[BasePlayer]):
        self.players = players
        self.theory_of_mind = {}
        for player in players:
            self.theory_of_mind[player] = 'No information available'
    
    def update(self, player: BasePlayer, reflection: str):
        self.theory_of_mind[player.name] = reflection

    def update_all(self, new_theory_of_mind: dict):
        self.theory_of_mind = new_theory_of_mind

    def get(self, player: BasePlayer):
        return self.theory_of_mind[player.name]

    def format_all(self):
        return '\n'.join([f'{player.name}: {reflection}' for player, reflection in self.theory_of_mind.items()])

        