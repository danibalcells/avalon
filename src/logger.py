import logging
from typing import List

class GameLogger:
    def __init__(self):
        self.events: List[str] = []
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log(self, event: str):
        self.events.append(event)
        logging.info(event)

    def get_events(self) -> List[str]:
        return self.events