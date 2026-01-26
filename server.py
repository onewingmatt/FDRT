from track_graph import get_track_graph


async def perform_slipstream_check(game_id: str):
    """
    Checks for and executes slipstream opportunities for players.
    Applies bonus movement, lane changes, and any associated penalties.
    """
    game = games[game_id]
    track = game.state.track
    
    # Sort players by distance to process in order
    players_to_check = sorted(
        [p for p in game.state.players if not p.is_eliminated],
        key=lambda p: (p.total_distance, -p.current_gear) 
    )
    
    slipstream_execution_results = {} 
    players_who_slipped_this_turn = set() 

    for p1 in players_to_check:
        if p1.id in players_who_slipped_this_turn: continue 

        # --- Check Slipstream Conditions ---
        if p1.current_gear < 4 or p1.is_eliminated:
            continue

        slipstream_target = None
        for p2 in players_to_check:
            if p1.id == p2.id: continue 

            # Condition: Directly behind another car.
            if p1.current_lane == p2.current_lane and \
               p2.current_space < p1.current_space <= p2.current_space + 3 and \
               p1.current_space > p2.current_space:
                
                slipstream_target = p2
                break 

        if slipstream_target:
            bonus_movement_required = 3
            print(f"Player {p1.id} qualifies for slipstream behind Player {slipstream_target.id}.")
            
            # --- Determine Valid Slipstream Moves ---
            valid_moves = find_valid_slipstream_moves(p1, slipstream_target, track, game.state)
            
            if not valid_moves:
                print(f"Player {p1.id} qualified but no valid slipstream moves found.")
                continue 

            # --- Choose Slipstream Move ---
            chosen_move_details = choose_slipstream_move(p1, valid_moves, game.state) 
            
            if not chosen_move_details:
                print(f"Player {p1.id} could not choose a valid slipstream move.")
                continue

            # --- Execute Slipstream Move ---
            penalty_wp = execute_slipstream_move(p1, chosen_move_details, track, game.state)
            
            p1.slipstream_bonus_granted = True 
            p1.slipstream_bonus_movement = bonus_movement_required 
            
            print(f"Player {p1.id} executed slipstream move, ending at space {p1.current_space} lane {p1.current_lane}.")
            if penalty_wp > 0:
                print(f"Player {p1.id} incurred {penalty_wp} penalty.")
            
            slipstream_execution_results[p1.id] = {'move_details': chosen_move_details, 'target_player_id': slipstream_target.id, 'penalty': penalty_wp}
            
            players_who_slipped_this_turn.add(p1.id)

            # Reset player's slipstream status for the next turn.
            p1.slipstream_bonus_granted = False 
            p1.slipstream_bonus_movement = 0

    # After processing all players, broadcast the state and transition to the next phase.
    await broadcast_state(game_id)
    await asyncio.sleep(1) 
    
    game.state.current_phase = GamePhase.COLLISION_CHECK

# --- HELPER FUNCTIONS FOR SLIPSTREAM MOVEMENT ---

async def find_valid_slipstream_moves(player, target_player, track, game_state):
    """Return move options that emulate valid slipstream paths."""
    possible_moves = []
    base_movement = 3

    start_space_id = player.current_space
    start_lane = player.current_lane
    start_space_obj = track.get_space(start_space_id)
    if not start_space_obj:
        return []

    player_positions = {
        p.id: {'space': p.current_space, 'lane': p.current_lane}
        for p in game_state.players if not p.is_eliminated
    }

    track_graph = get_track_graph(track)
    paths = track_graph.walk(start_space_id, base_movement)
    seen_endpoints = set()

    for path in paths:
        if not is_path_clear(path, player_positions, player.id, track_graph):
            continue

        final_space_id = path[-1]
        final_space_obj = track_graph.get_space(final_space_id)
        if not final_space_obj:
            continue

        endpoint = (final_space_obj.id, final_space_obj.lane)
        if endpoint in seen_endpoints:
            continue
        seen_endpoints.add(endpoint)

        move_type = determine_slipstream_move_type(
            track_graph, path, start_lane, player, target_player
        )
        penalty = 1 if final_space_obj.corner_zone else 0

        possible_moves.append({
            'type': move_type,
            'final_space_id': final_space_obj.id,
            'final_lane': final_space_obj.lane,
            'penalty': penalty,
            'spaces_moved': base_movement,
            'path': path.copy()
        })

    print(f"Found {len(possible_moves)} potential slipstream moves for player {player.id}.")
    return possible_moves


def is_path_clear(path, player_positions, current_player_id, track_graph):
    for space_id in path[1:]:
        space_obj = track_graph.get_space(space_id)
        if not space_obj:
            return False

        for other_player_id, pos in player_positions.items():
            if other_player_id == current_player_id:
                continue
            if pos['space'] == space_id and pos['lane'] == space_obj.lane:
                return False

    return True


def determine_slipstream_move_type(track_graph, path, start_lane, player, target_player):
    lane_sequence = track_graph.iter_space_lanes(path)
    lane_changes = sum(
        1 for i in range(1, len(lane_sequence)) if lane_sequence[i] != lane_sequence[i - 1]
    )
    final_lane = lane_sequence[-1] if lane_sequence else start_lane
    spaces_moved = len(path) - 1
    anticipated_distance = player.total_distance + spaces_moved
    is_overtake = target_player and anticipated_distance > target_player.total_distance

    if lane_changes == 0 and final_lane == start_lane:
        return 'straight_move'
    if is_overtake:
        return 'overtake'
    return 'lane_change'


def choose_slipstream_move(player, available_moves, game_state):
    """
    Chooses the best slipstream move from available options.
    Bots should consider safety, speed, and positioning.
    """
    if not available_moves: return None
    
    # Basic bot choice: Pick the first valid move.
    # A real bot would analyze options (e.g., prioritizing overtaking if safe and beneficial).
    # Strategy: Prefer overtake moves if available and safe. 
    
    overtake_moves = [m for m in available_moves if m['type'] == 'overtake']
    if overtake_moves:
        print(f"Bot choosing overtake slipstream move.")
        return overtake_moves[0]
    else:
        # If no overtake, pick the first available (e.g., straight or lane change).
        chosen_move = available_moves[0] 
        print(f"Bot choosing simplified move: {chosen_move}")
        return chosen_move

def execute_slipstream_move(player, move_details, track, game_state):
    """Applies the chosen slipstream move to the player's state."""
    player.current_space = move_details['final_space_id']
    player.current_lane = move_details['final_lane']
    player.total_distance += move_details['spaces_moved'] 
    
    penalty = move_details.get('penalty', 0)
    if penalty > 0:
        player.damage.take_damage("brakes", penalty) 
    
    return penalty 

# --- Helper function to check move validity (needed by find_valid_slipstream_moves) ---
def is_move_valid(target_space_id, target_lane, current_player_id, track, game_state):
    """
    Checks if a potential move is valid, considering track bounds, collisions, and rules.
    """
    # Check lane bounds (assuming num_lanes_at_start is available or determined per space)
    target_space_obj = track.get_space(target_space_id)
    if not target_space_obj: return False
    num_lanes = getattr(target_space_obj, 'total_lanes', 3) # Default to 3 lanes
    if not (0 <= target_lane < num_lanes):
        return False

    # Check for collisions with other players in the target space and lane
    for other_player in game_state.players:
        if other_player.id == current_player_id or other_player.is_eliminated: continue
        if other_player.current_space == target_space_id and other_player.current_lane == target_lane:
            return False # Collision detected

    # TODO: Add checks for track arrows, specific space rules, etc.
    return True

# --- Update make_bot_decisions ---
# Add logic for bots to actively choose slipstream moves if beneficial.

# --- Update check_all_players_ready ---
# It correctly calls perform_slipstream_check. The phase transition is handled within perform_slipstream_check.

# --- Update broadcast_state ---
# Ensure slipstream info is sent (already done via Player.to_dict).
