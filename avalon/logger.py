from dataclasses import dataclass
import logging
from typing import List, TypeVar
from enum import Enum

PlayerType = TypeVar('PlayerType', bound='BasePlayer')

@dataclass
class EventVisibility(Enum):
    PUBLIC = "PUBLIC"
    EVIL = "EVIL"
    PRIVATE = "PRIVATE"
    ADMIN = "ADMIN"

@dataclass
class Event():
    message: str
    visibility: EventVisibility
    players: List[PlayerType]

def format_events(events: List[Event]):
    return '\n'.join([e.message for e in events])

class GameLogger:
    def __init__(self):
        self.events: List[Event] = []
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )

    def log_public(self, message: str):
        self.events.append(Event(message, EventVisibility.PUBLIC.value, players=[]))
        logging.info(message)

    def log_evil(self, message: str):
        self.events.append(Event(message, EventVisibility.EVIL.value, players=[]))
        logging.info(message)

    def log_private(self, message: str, player: PlayerType):
        self.events.append(Event(message, EventVisibility.PRIVATE.value, players=[player]))
        logging.info(message)

    def log_admin(self, message: str):
        self.events.append(Event(message, EventVisibility.ADMIN.value, players=[]))
        logging.info(message)

    def get_events_filtered(self, allowed_visibilities: List[EventVisibility]) -> List[Event]:
        return [e for e in self.events if e.visibility in allowed_visibilities]

    def get_public_events(self) -> List[Event]:
        allowed_visibilities = [EventVisibility.PUBLIC.value]
        return self.get_events_filtered(allowed_visibilities)

    def get_evil_events(self) -> List[Event]:
        allowed_visibilities = [EventVisibility.PUBLIC.value, EventVisibility.EVIL.value]
        return self.get_events_filtered(allowed_visibilities)

    def get_admin_events(self) -> List[Event]:
        allowed_visibilities = [EventVisibility.PUBLIC.value, EventVisibility.EVIL.value, EventVisibility.ADMIN.value]
        return self.get_events_filtered(allowed_visibilities)

    def get_player_events(self, player: PlayerType) -> List[Event]:
        allowed_visibilities = [EventVisibility.PUBLIC.value]
        if player.is_evil:
            allowed_visibilities.append(EventVisibility.EVIL.value)
        return [e for e in self.events if player in e.players or e.visibility in allowed_visibilities]