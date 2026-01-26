"""
Formula D Online - Core Game Engine
Supports 1-8 players with simultaneous turn resolution
"""

import json
import random
from enum import Enum
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import random

# Constants
GEAR_DICE = {
    1: (1, 4),   # d4
    2: (1, 6),   # d6
    3: (1, 8),   # d8
    4: (1, 12),  # d12
    5: (1, 20),  # d20
    6: (1, 30)   # d30
}

class SpaceType(Enum):
    NORMAL = "normal"
    CORNER = "corner"
    START = "start"
    FINISH = "finish"

class DiceMode(Enum):
    SIMPLE = "simple"
    REALISTIC = "realistic"

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

    def get_space(self, space_id: int) -> Optional[TrackSpace]:
        for space in self.spaces:
            if space.id == space_id:
                return space
        return None

    @staticmethod
    def load_from_json(filepath: str):
        """Load track from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        spaces = [
            TrackSpace(
                id=s["id"],
                x=s["x"],
                y=s["y"],
                lane=s["lane"],
                space_type=SpaceType(s["space_type"]),
                corner_zone=s.get("corner_zone"),
                corner_stops_required=s.get("corner_stops_required", 0),
                connected_spaces=s.get("connected_spaces", [])
            )
            for s in data["spaces"]
        ]

        corners = [
            CornerZone(
                name=c["name"],
                color=c["color"],
                stops_required=c["stops_required"],
                spaces=c["spaces"]
            )
            for c in data["corners"]
        ]

        return Track(
            name=data["name"],
            spaces=spaces,
            corners=corners,
            start_positions=data["start_positions"],
            lap_length=data["lap_length"]
        )

@dataclass
class DamageTrack:
    """Tracks damage for different car systems"""
    engine: int = 18
    brakes: int = 18
    tires: int = 18
    body: int = 18
    handling: int = 3

    def take_damage(self, damage_type: str, amount: int) -> bool:
        """Apply damage, return True if car is still operational"""
        if hasattr(self, damage_type):
            current = getattr(self, damage_type)
            setattr(self, damage_type, max(0, current - amount))

            if damage_type == "handling" and getattr(self, damage_type) == 0:
                return False
            if damage_type == "engine" and getattr(self, damage_type) == 0:
                return False
        return True

@dataclass
class Player:
    """Player state"""
    id: int
    name: str
    current_space: int
    current_gear: int = 1
    next_gear: Optional[int] = None
    damage: DamageTrack = field(default_factory=DamageTrack)
    corner_stops: Dict[str, int] = field(default_factory=dict)
    is_eliminated: bool = False
    lap: int = 0
    total_distance: int = 0
    last_roll: Optional[int] = None

class GamePhase(Enum):
    GEAR_SELECTION = "gear_selection"
    DICE_ROLL = "dice_roll"
    MOVEMENT = "movement"
    COLLISION_CHECK = "collision_check"
    CORNER_VALIDATION = "corner_validation"
    TURN_END = "turn_end"

@dataclass
class GameState:
    track: Track
    players: List[Player]
    current_turn: int = 0
    current_phase: GamePhase = GamePhase.GEAR_SELECTION
    race_started: bool = False
    race_finished: bool = False
    winner: Optional[int] = None
    dice_mode: DiceMode = DiceMode.REALISTIC  # Default to realistic

class FormulaGame:
    """Main game engine - handles all game logic"""

    def __init__(self, track: Track, player_names: List[str]):
        self.state = GameState(track=track, players=[], dice_mode=DiceMode.REALISTIC)
        self.dice_system = DiceSystem(DiceMode.REALISTIC)
        for i, name in enumerate(player_names[:8]):
            self.state.players.append(Player(
                id=i,
                name=name,
                current_space=track.start_positions[i],
                current_gear=0
            ))
    
    def set_dice_mode(self, mode: DiceMode):
        """Set the dice mode for this game"""
        self.state.dice_mode = mode
        self.dice_system = DiceSystem(mode)
    
    def roll_die(self, gear: int) -> int:
        """Roll die for a specific gear using current dice system"""
        return self.dice_system.roll_gear(gear)

    def can_shift_to_gear(self, player: Player, target_gear: int) -> Tuple[bool, str]:
        """Check if player can shift to target gear"""
        current = player.current_gear

        if target_gear == current + 1:
            return True, "OK"

        if target_gear < current and target_gear >= 1:
            gears_down = current - target_gear
            if gears_down <= 3:
                damage = gears_down
                if player.damage.brakes >= damage:
                    return True, f"Downshift {gears_down} gears (-{damage} brake WP)"
                else:
                    return False, "Insufficient brake WP"
            else:
                return False, "Can only downshift max 3 gears"

        if target_gear > current + 1:
            return False, "Cannot skip gears when shifting up"

        return False, "Invalid gear"

    def add_player(self, player_name: str) -> Optional[int]:
        """Add a new player to game (before race starts)"""
        if self.state.race_started:
            return None
        
        new_id = len(self.state.players)
        if new_id >= 8:  # Max 8 players
            return None
        
        # Check for name conflicts
        if any(p.name == player_name for p in self.state.players):
            return None
        
        # Find next available starting position
        if new_id < len(self.state.track.start_positions):
            start_pos = self.state.track.start_positions[new_id]
        else:
            start_pos = 0  # Fallback to first position
        
        # Add new player
        new_player = Player(
            id=new_id,
            name=player_name,
            current_space=start_pos,
            current_gear=0
        )
        
        self.state.players.append(new_player)
        return new_id

class DiceSystem:
    """Handles both simple and realistic dice rolling mechanics"""
    
    def __init__(self, mode: DiceMode = DiceMode.REALISTIC, seed: Optional[int] = None):
        self.mode = mode
        self.rng = random.Random(seed)
        self._setup_dice_faces()
    
    def _setup_dice_faces(self):
        """Initialize dice face distributions based on mode"""
        if self.mode == DiceMode.SIMPLE:
            self.dice_faces = {
                1: (1, 4),   # d4 - Range: 1-4
                2: (1, 6),   # d6 - Range: 1-6
                3: (1, 8),   # d8 - Range: 1-8
                4: (1, 12),  # d12 - Range: 1-12
                5: (1, 20),  # d20 - Range: 1-20
                6: (1, 30)   # d30 - Range: 1-30
            }
        elif self.mode == DiceMode.REALISTIC:
            # Official Formula D dice distributions (weighted)
            self.dice_faces = {
                1: [1, 1, 2, 2],    # Special d4 - favors 1-2
                2: [2, 2, 3, 3, 4, 4],  # Weighted d6 - favors 2-4
                3: [4, 5, 6, 6, 7, 8],  # Weighted d8 - favors 5-8
                4: [7, 7, 8, 9, 10, 11, 12],  # Weighted d12 - favors 7-12
                5: [11, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],  # Weighted d20 - favors 11-20
                6: [21, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]  # Weighted d30 - favors 21-30
            }
    
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

    def add_bot(self, difficulty: str = "easy") -> Optional[int]:
        """Add a bot player with specified difficulty"""
        bot_names = ["Speedster", "Racer X", "Thunder", "Lightning", "Shadow", "Blaze", "Viper", "Storm"]
        bot_name = f"[BOT] {random.choice(bot_names)}"
        
        # Create new player and add to game
        new_id = len(self.state.players)
        if new_id >= 8:  # Max 8 players
            return None
        
        # Check for name conflicts
        if any(p.name == bot_name for p in self.state.players):
            return None
        
        # Find next available starting position
        start_pos = 0  # Fallback to first position
        try:
            if hasattr(self.state, 'track') and hasattr(self.state.track, 'start_positions') and new_id < len(self.state.track.start_positions):
                start_pos = self.state.track.start_positions[new_id]
        except AttributeError:
            pass  # Skip if track not initialized
        
        # Add new player
        new_player = Player(
            id=new_id,
            name=bot_name,
            current_space=start_pos,
            current_gear=0
        )
        
        self.state.players.append(new_player)
        return new_id

    def is_bot_player(self, player_name: str) -> bool:
        """Check if player is a bot"""
        return player_name is not None and player_name.startswith("[BOT]")

    def to_dict(self) -> dict:
        """Serialize game state for network transmission"""
        return {
            "current_turn": self.state.current_turn,
            "current_phase": self.state.current_phase.value,
            "race_started": self.state.race_started,
            "race_finished": self.state.race_finished,
            "winner": self.state.winner,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "current_space": p.current_space,
                    "current_gear": p.current_gear,
                    "next_gear": getattr(p, 'next_gear', None),
                    "lap": p.lap,
                    "total_distance": p.total_distance,
                    "last_roll": getattr(p, 'last_roll', None),
                    "corner_stops": getattr(p, 'corner_stops', {}),
                    "is_eliminated": p.is_eliminated,
                    "is_bot": False,  # Will be set in server during serialization
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
    'GEAR_DICE', 'SpaceType', 'DamageTrack', 'DiceMode', 'DiceSystem'
]
