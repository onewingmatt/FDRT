"""
Formula D Online - Core Game Engine with Dual Dice System
Supports 1-8 players with simultaneous turn resolution
"""

import json
import random
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# Constants
GEAR_DICE = {
    1: (1, 4),   # d4
    2: (1, 6),   # d6
    3: (1, 8),   # d8
    4: (1, 12),  # d12
    5: (1, 20),  # d20
    6: (1, 30)   # d30
}

# New realistic weighted dice distributions based on official Formula D rules
REALISTIC_GEAR_DICE = {
    1: (1, 2),   # Special d4 - favors 1-2
    2: (2, 2, 3, 3, 4, 4),  # Weighted d6 - favors 2-4
    3: (4, 5, 6, 6, 7, 8),  # Weighted d8 - favors 5-8
    4: (7, 7, 8, 9, 10, 11, 12),  # Weighted d12 - favors 7-12
    5: (11, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20),  # Weighted d20 - favors 11-20
    6: (21, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30)  # Weighted d30 - favors 21-30
}

class SpaceType(Enum):
    NORMAL = "normal"
    CORNER = "corner"
    START = "start"
    FINISH = "finish"

class GamePhase(Enum):
    GEAR_SELECTION = "gear_selection"
    DICE_ROLL = "dice_roll"
    MOVEMENT = "movement"
    COLLISION_CHECK = "collision_check"
    CORNER_VALIDATION = "corner_validation"
    TURN_END = "turn_end"

class DiceMode(Enum):
    SIMPLE = "simple"
    REALISTIC = "realistic"

class DiceSystem:

class DiceSystem:

class DiceMode(Enum):
    SIMPLE = "simple"
    REALISTIC = "realistic"

@dataclass
class Player:
    """Player state"""
    id: int
    name: str
    current_space: int
    current_gear: int = 1
    next_gear: Optional[int] = None
    lap: int = 0
    total_distance: int = 0
    last_roll: Optional[int] = None
    corner_stops: Dict[str, int] = field(default_factory=dict)
    is_eliminated: bool = False
    damage: 'DamageTrack'
    is_bot: bool = False

@dataclass 
class DamageTrack:
    """Tracks damage for different car systems"""
    engine: int = 18
    brakes: int = 18
    tires: int = 18
    body: int = 18
    handling: int = 3

@dataclass
class TrackSpace:
    """Represents a single space on the track"""
    id: int
    x: float
    y: float
    lane: int
    space_type: SpaceType
    corner_zone: Optional[str] = None
    corner_stops_required: int = 0
    connected_spaces: List[int] = field(default_factory=list)

@dataclass
class CornerZone:
    """Defines a corner section with stop requirements"""
    name: str
    color: str
    stops_required: int
    spaces: List[int]

@dataclass
class Track:
    """Complete track definition - can be loaded from JSON"""
    name: str
    spaces: List[TrackSpace]
    corners: List[CornerZone]
    start_positions: List[int]
    lap_length: int

@dataclass
class GameState:
    """Main game state"""
    track: Track
    players: List[Player]
    current_turn: int = 0
    current_phase: 'GamePhase' = GamePhase.GEAR_SELECTION
    race_started: bool = False
    race_finished: bool = False
    winner: Optional[int] = None
    dice_mode: DiceMode = DiceMode.REALISTIC

class DiceSystem:
    """Handles both simple and realistic dice rolling mechanics"""
    
    def __init__(self, mode: DiceMode = DiceMode.REALISTIC, seed: Optional[int] = None):
        self.mode = mode
        self.rng = random.Random(seed)
        self._setup_dice_faces()
    
    def _setup_dice_faces(self):
        """Initialize dice face distributions based on mode"""
        if self.mode == DiceMode.SIMPLE:
            self.dice_faces = GEAR_DICE
        elif self.mode == DiceMode.REALISTIC:
            self.dice_faces = REALISTIC_GEAR_DICE
        else:
            raise ValueError(f"Unknown dice mode: {self.mode}")
    
    def roll_gear(self, gear: int) -> int:
        """Roll dice based on gear and current dice mode"""
        if gear not in self.dice_faces:
            return 1  # Default fallback
        
        faces = self.dice_faces[gear]
        return self.rng.choice(faces)
    
    def get_gear_range(self, gear: int) -> Tuple[int, int]:
        """Get min/max values for gear explanation"""
        if gear not in self.dice_faces:
            return (1, 1)
        
        faces = self.dice_faces[gear]
        return (min(faces), max(faces))
    
    def get_gear_distribution_description(self, gear: int) -> str:
        """Get description of dice distribution for UI display"""
        if self.mode == DiceMode.SIMPLE:
            return f"Uniform d{GEAR_DICE[gear][1]} (1-{GEAR_DICE[gear][1]})"
        elif self.mode == DiceMode.REALISTIC:
            faces = self.dice_faces[gear]
            return f"Weighted d{GEAR_DICE[gear][1]} ({min(faces)}-{max(faces)})"
        else:
            return "Unknown mode"

class FormulaGame:
    """Main game engine - handles all game logic"""

    def __init__(self, track: Track, player_names: List[str]):
        self.state = GameState(track=track, players=[])
        self.dice_system = DiceSystem(DiceMode.REALISTIC)  # Default to realistic
        
        for i, name in enumerate(player_names[:8]):
            self.state.players.append(Player(
                id=i,
                name=name,
                current_space=track.start_positions[i] if i < len(track.start_positions) else 0,
                current_gear=1,
                is_bot=False
            ))

    def set_dice_mode(self, mode: DiceMode):
        """Set dice mode for this game"""
        self.state.dice_mode = mode
        self.dice_system = DiceSystem(mode)

    def roll_die(self, gear: int) -> int:
        """Roll die for a specific gear using current dice system"""
        return self.dice_system.roll_gear(gear)

    def to_dict(self) -> dict:
        """Serialize game state for network transmission"""
        return {
            "current_turn": self.state.current_turn,
            "current_phase": self.state.current_phase.value,
            "race_started": self.state.race_started,
            "race_finished": self.state.race_finished,
            "winner": self.state.winner,
            "dice_mode": self.state.dice_mode.value,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "current_space": p.current_space,
                    "current_gear": p.current_gear,
                    "lap": p.lap,
                    "total_distance": p.total_distance,
                    "last_roll": p.last_roll,
                    "corner_stops": p.corner_stops,
                    "is_eliminated": p.is_eliminated,
                    "is_bot": p.is_bot,
                    "damage": {
                        "engine": p.damage.engine,
                        "brakes": p.damage.brakes,
                        "tires": p.damage.tires,
                        "body": p.damage.body,
                        "handling": p.damage.handling
                    }
                }
                for p in self.state.players
            ]
        }

# Export key classes
__all__ = [
    'FormulaGame', 'Track', 'Player', 'GamePhase', 
    'GEAR_DICE', 'SIMPLE_GEAR_DICE', 'REALISTIC_GEAR_DICE',
    'SpaceType', 'DamageTrack', 'TrackSpace', 'CornerZone', 'DiceMode', 'DiceSystem'
]