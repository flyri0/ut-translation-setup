from dataclasses import dataclass
from typing import Optional


@dataclass
class AppState:
    game_path: Optional[str] = None