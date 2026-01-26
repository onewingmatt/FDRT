"""
Lane mechanics for Formula D
"""
from typing import List, Tuple, Optional
from formula_d_game import Player, Track, TrackSpace

def calculate_valid_lanes(current_space: TrackSpace, track: Track, movement: int) -> List[int]:
    """Calculate which lanes are reachable with up to 2 lane changes"""
    if not current_space:
        return [0]
    
    valid_lanes = set()
    max_lanes = getattr(current_space, 'total_lanes', 3) - 1
    
    # Current lane is always valid
    valid_lanes.add(current_space.lane)
    
    # Can move 1 lane (1 change)
    if current_space.lane > 0:
        valid_lanes.add(current_space.lane - 1)
    if current_space.lane < max_lanes:
        valid_lanes.add(current_space.lane + 1)
    
    # Can move 2 lanes (2 changes) if moving far enough
    if movement >= 3:  # Need distance to make 2 lane changes
        valid_lanes.add(0)  # Inside
        valid_lanes.add(1)  # Middle  
        valid_lanes.add(max_lanes)  # Outside
    
    return sorted(list(valid_lanes))

def get_target_space(track: Track, current_space_id: int, movement: int, target_lane: int) -> Optional[int]:
    """Find the space ID at the target position and lane"""
    current_space = track.get_space(current_space_id)
    if not current_space:
        return None
    
    # Simple forward movement based on connected spaces
    target_space_id = current_space_id + movement
    
    # Find the space with matching target lane near target position
    search_range = 5  # Search within 5 spaces forward/backward
    for offset in range(-search_range, search_range + 1):
        test_space_id = (target_space_id + offset) % len(track.spaces)
        test_space = track.get_space(test_space_id)
        
        if test_space and hasattr(test_space, 'lane') and test_space.lane == target_lane:
            return test_space_id
    
    # If no exact lane match, return closest forward space
    return target_space_id % len(track.spaces)

def format_lane_name(lane: int) -> str:
    """Get human-readable lane name"""
    lane_names = {0: "Inside", 1: "Middle", 2: "Outside"}
    return lane_names.get(lane, f"Lane {lane}")

