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
    LANE_SELECTION = "lane_selection" # Added for lane selection phase
    DICE_ROLL = "dice_roll"
    MOVEMENT = "movement"
    SLIPSTREAM_CHECK = "slipstream_check" # New phase for slipstreaming
    COLLISION_CHECK = "collision_check"
    CORNER_VALIDATION = "corner_validation"
    TURN_END = "turn_end"

class DiceMode(Enum):
    SIMPLE = "simple"
    REALISTIC = "realistic"

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

@dataclass
class Player:
    """Player state"""
    id: int
    name: str
    current_space: int
    damage: 'DamageTrack'
    current_gear: int = 1
    next_gear: Optional[int] = None
    lap: int = 0
    total_distance: int = 0
    last_roll: Optional[int] = None
    corner_stops: Dict[str, int] = field(default_factory=dict)
    is_eliminated: bool = False
    is_bot: bool = False
    # Lane selection attributes
    current_lane: int = field(default=1)
    next_lane: Optional[int] = None
    # Slipstream attributes
    slipstream_bonus_granted: bool = field(default=False)
    slipstream_bonus_movement: int = field(default=0)

@dataclass 
class DamageTrack:
    """Tracks damage for different car systems"""
    engine: int = 18
    brakes: int = 18
    tires: int = 18
    body: int = 18
    handling: int = 3
    
    def take_damage(self, system: str, amount: int):
        """Apply damage to a specific system"""
        if system == "engine":
            self.engine = max(0, self.engine - amount)
        elif system == "brakes":
            self.brakes = max(0, self.brakes - amount)
        elif system == "tires":
            self.tires = max(0, self.tires - amount)
        elif system == "body":
            self.body = max(0, self.body - amount)
        elif system == "handling":
            self.handling = max(0, self.handling - amount)
    
    def is_critical_damage(self) -> bool:
        """Check if any system has critical damage"""
        return any([
            self.engine <= 0,
            self.brakes <= 0,
            self.tires <= 0,
            self.body <= 0,
            self.handling <= 0
        ])

@dataclass
class TrackSpace:
    """Represents a single space on the track"""
    id: int
    x: float
    y: float
    lane: int
    space_type: SpaceType
    total_lanes: int # Added for variable lane counts per space
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
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'Track':
        """Load track from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert spaces
        spaces = []
        for space_data in data.get('spaces', []):
            space = TrackSpace(
                id=space_data['id'],
                x=space_data['x'],
                y=space_data['y'],
                lane=space_data.get('lane', 1),
                space_type=SpaceType(space_data.get('space_type', 'normal')),
                corner_zone=space_data.get('corner_zone'),
                corner_stops_required=space_data.get('corner_stops_required', 0),
                connected_spaces=space_data.get('connected_spaces', []),
                total_lanes=space_data.get('total_lanes', 3) # Read from JSON
            )
            spaces.append(space)
        
        # Convert corners
        corners = []
        for corner_data in data.get('corners', []):
            corner = CornerZone(
                name=corner_data['name'],
                color=corner_data['color'],
                stops_required=corner_data['stops_required'],
                spaces=corner_data['spaces']
            )
            corners.append(corner)
        
        return cls(
            name=data['name'],
            spaces=spaces,
            corners=corners,
            start_positions=data['start_positions'],
            lap_length=data['lap_length']
        )
    
    def get_space(self, space_id: int) -> Optional[TrackSpace]:
        """Get space by ID"""
        for space in self.spaces:
            if space.id == space_id:
                return space
        return None

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
                damage=DamageTrack(),
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
    
    def add_player(self, name: str) -> Optional[int]:
        """Add a new player to the game"""
        player_id = len(self.state.players)
        if player_id >= 8:
            return None  # Max players reached
        
        # Find next available start position
        start_pos = self.state.track.start_positions[player_id] if player_id < len(self.state.track.start_positions) else 0
        
        new_player = Player(
            id=player_id,
            name=name,
            current_space=start_pos,
            damage=DamageTrack(),
            current_gear=1,
            is_bot=False
        )
        
        self.state.players.append(new_player)
        return player_id
    
    def add_bot(self, difficulty: str = "easy") -> Optional[int]:
        """Add a bot player to the game"""
        bot_name = f"[BOT] {difficulty.capitalize()} {len(self.state.players) + 1}"
        return self.add_player(bot_name)
    
    def can_shift_to_gear(self, player: Player, target_gear: int) -> Tuple[bool, str]:
        """Check if player can shift to target gear"""
        if target_gear < 0 or target_gear > 6:
            return False, "Invalid gear"
        
        current = player.current_gear
        
        # Can always shift down 1 gear
        if target_gear == current - 1:
            return True, "Downshift"
        
        # Can shift up 1 gear per turn
        if target_gear == current + 1:
            return True, "Upshift"
        
        # From neutral (0) can only go to 1st
        if current == 0 and target_gear == 1:
            return True, "Start from neutral"
        
        # Special: downshift multiple gears (takes extra time and causes damage)
        if target_gear < current - 1:
            damage = current - target_gear - 1
            return True, f"Downshift {damage} damage"
        
        return False, "Gear shift not allowed"

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
                    "current_lane": p.current_lane,
                    "next_lane": p.next_lane,
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
    'GEAR_DICE', 'REALISTIC_GEAR_DICE',
    'SpaceType', 'DamageTrack', 'TrackSpace', 'CornerZone', 'DiceMode', 'DiceSystem'
]