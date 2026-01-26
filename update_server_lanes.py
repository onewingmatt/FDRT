# Add to server.py after the imports:

# Store lane selections
lane_selections: Dict[str, Dict[int, int]] = {}

# In websocket gear_selection handler, capture lane:
# lane = data.get("lane")
# if lane is not None:
#     if game_id not in lane_selections:
#         lane_selections[game_id] = {}
#     lane_selections[game_id][player_id] = lane

# Update move_player function:
def move_player_with_lane(game: FormulaGame, player, target_lane: int = None):
    """Move a player with lane selection"""
    if player.last_roll is None or player.last_roll == 0:
        return
    
    spaces_to_move = player.last_roll
    current_lane = player.current_space % 3
    
    # Use target lane if provided, otherwise keep current
    if target_lane is None:
        target_lane = current_lane
    
    # Validate lane changes (max 2)
    lane_changes = abs(target_lane - current_lane)
    if lane_changes > 2:
        target_lane = current_lane  # Invalid, stay in lane
    
    # Calculate new position
    current_row = player.current_space // 3
    target_row = current_row + spaces_to_move
    
    # Wrap for lap
    max_rows = len(game.state.track.spaces) // 3
    if target_row >= max_rows:
        target_row = target_row % max_rows
        player.lap += 1
    
    # New space ID: row * 3 + lane
    player.current_space = (target_row * 3) + target_lane
    player.total_distance += spaces_to_move
    
    # Track corners
    new_space = game.state.track.get_space(player.current_space)
    if new_space and new_space.corner_zone:
        if new_space.corner_zone not in player.corner_stops:
            player.corner_stops[new_space.corner_zone] = 0
        player.corner_stops[new_space.corner_zone] += 1
    
    player.last_roll = None

