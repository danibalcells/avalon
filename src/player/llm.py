from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, TypeVar
import logging
import random
from .base import BasePlayer

PlayerType = TypeVar('PlayerType', bound='BasePlayer')

class LLMPlayer(BasePlayer):
    def __init__(self, name: str, game: 'Game'):
        super().__init__(name, game)
        self.llm_chain = self.create_llm_chain()

    def create_llm_chain(self) -> LLMChain:
        # Initialize your LLMChain here
        prompt_template = PromptTemplate(
            input_variables=["prompt"],
            template="You are playing a game of Avalon. {prompt}"
        )
        llm_chain = LLMChain(prompt_template=prompt_template)
        return llm_chain

    def propose_team(self, num_players: int) -> List[PlayerType]:
        prompt = f"Propose a team of {num_players} players for the quest. Here are the players: {[player.name for player in self.game.players]}"
        response = self.llm_chain.run(prompt)
        team_names = response.split(", ")
        team = [player for player in self.game.players if player.name in team_names]
        logging.info(f"{self} proposed team: {[str(player) for player in team]}")
        return team

    def vote_on_team(self, team: List[PlayerType]) -> bool:
        prompt = f"Vote on the proposed team: {[player.name for player in team]}. Here are the previous votes: {self.game.vote_history}"
        response = self.llm_chain.run(prompt)
        vote = response.strip().lower() == 'yes'
        logging.info(f"{self} voted {'Yes' if vote else 'No'}")
        return vote

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        prompt = f"Conduct the quest with the team: {[player.name for player in team]}. You are {'Loyal' if self.is_loyal else 'Evil'}."
        response = self.llm_chain.run(prompt)
        success = response.strip().lower() == 'success'
        logging.info(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success