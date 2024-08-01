from typing import List, TypeVar
import logging

from langchain_openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from avalon.player.base import BasePlayer
from avalon.logger import format_events

PlayerType = TypeVar('PlayerType', bound='BasePlayer')
DEF_PROMPT_PATH = 'avalon/templates/llm_player'

class LLMPlayer(BasePlayer):
    def __init__(self, name: str, player_id: int, game: 'Game', prompt_path: str = DEF_PROMPT_PATH):
        super().__init__(name, player_id, game)
        self.load_prompts(prompt_path)
        self.create_llm_chains()

    def load_prompts(self, prompt_path: str):
        with open(prompt_path + '/base.txt') as f:
            base_prompt_str = f.read()
        with open(prompt_path + '/choose_team.txt') as f:
            choose_team_prompt_str = f.read()
            self.choose_team_prompt_template = ChatPromptTemplate.from_template(base_prompt_str + 
                                                                                choose_team_prompt_str)
        with open(prompt_path + '/vote_team.txt') as f:
            vote_team_prompt_str = f.read()
            self.vote_team_prompt_template = ChatPromptTemplate.from_template(base_prompt_str + 
                                                                                vote_team_prompt_str)
        with open(prompt_path + '/conduct_quest.txt') as f:
            conduct_quest_prompt_str = f.read()
            self.conduct_quest_prompt_template = ChatPromptTemplate.from_template(base_prompt_str + 
                                                                                conduct_quest_prompt_str)
    def create_llm_chains(self):
        self.llm = OpenAI()
        self.choose_team_chain = self.choose_team_prompt_template | self.llm | JsonOutputParser()
        self.vote_team_chain = self.vote_team_prompt_template | self.llm | JsonOutputParser()
        self.conduct_quest_chain = self.conduct_quest_prompt_template | self.llm | JsonOutputParser()

    def propose_team(self, num_players: int) -> List[PlayerType]:
        response = self.choose_team_chain.invoke({
            'player_name': self.name,
            'role': self.role,
            'allegiance': self.allegiance,
            'events': format_events(self.logger.get_player_events(self)),
            'n_players_in_quest': num_players,
            'n_quest': self.game.current_quest + 1,
            'attempt': self.game.rejected_teams + 1,
            'player_names': self.game.format_player_list()
        })
        self.logger.log_admin(f'True explanation: {response["true_explanation"]}')
        self.logger.log_admin(f'Public explanation: {response["public_explanation"]}')
        return self.game.get_players_by_ids(response['player_ids'])

    def vote_on_team(self, team: List[PlayerType]) -> bool:
        response = self.vote_team_chain.invoke({
            'player_name': self.name,
            'role': self.role,
            'allegiance': self.allegiance,
            'events': format_events(self.logger.get_player_events(self)),
            'player_names': self.game.format_player_list(team)
        })
        self.logger.log_admin(f'True explanation: {response["true_explanation"]}')
        self.logger.log_admin(f'Public explanation: {response["public_explanation"]}')
        return response['vote']

    def conduct_quest(self, team: List[PlayerType]) -> bool:
        response = self.conduct_quest_chain.invoke({
            'player_name': self.name,
            'role': self.role,
            'allegiance': self.allegiance,
            'events': format_events(self.logger.get_player_events(self)),
        })
        self.logger.log_admin(f'True explanation: {response["true_explanation"]}')
        self.logger.log_admin(f'Public explanation: {response["public_explanation"]}')
        success = bool(response['vote'])
        self.logger.log_admin(f"{self} {'succeeded' if success else 'failed'} the quest")
        return success