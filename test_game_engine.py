#!/usr/bin/env python3
"""Quick test of the Formula D game engine"""

from formula_d_game import FormulaGame, Track, DiceMode, DamageTrack
import pytest # Import pytest for assert functionality

def test_basic_functionality():
    print("Testing Formula D Game Engine...")
    
    # Load track (fallback to minimal if full track not available)
    try:
        track = Track.load_from_json("monaco_track_coordinates.json")
        print(f"✓ Loaded track: {track.name} with {len(track.spaces)} spaces")
    except Exception as e:
        # If track loading fails, this test should fail
        pytest.fail(f"Track loading failed: {e}")
    
    # Create game with 2 players
    game = FormulaGame(track, ["Player 1", "Player 2"])
    assert len(game.state.players) == 2, f"Expected 2 players, got {len(game.state.players)}"
    print(f"✓ Created game with {len(game.state.players)} players")
    
    # Test dice system
    assert game.state.dice_mode == DiceMode.REALISTIC, f"Initial dice mode expected REALISTIC, got {game.state.dice_mode.value}"
    print(f"✓ Dice mode: {game.state.dice_mode.value}")
    
    # Test gear shifting
    player = game.state.players[0]
    can_shift, reason = game.can_shift_to_gear(player, 2)
    assert can_shift is True, f"Player should be able to shift to gear 2, but couldn't: {reason}"
    print(f"✓ Gear shift test: {can_shift} - {reason}")
    
    # Test dice rolling (just ensure it returns a valid number)
    roll = game.roll_die(1)
    assert 1 <= roll <= 4, f"Dice roll for gear 1 should be between 1-4, got {roll}"
    print(f"✓ Dice roll in gear 1: {roll}")
    
    # Test damage system
    initial_engine_damage = player.damage.engine
    player.damage.take_damage("engine", 5)
    assert player.damage.engine == initial_engine_damage - 5, f"Engine damage not applied correctly. Expected {initial_engine_damage - 5}, got {player.damage.engine}"
    print(f"✓ Engine damage applied: {player.damage.engine}/18")
    
    # Test realistic vs simple dice
    game.set_dice_mode(DiceMode.REALISTIC)
    realistic_roll = game.roll_die(3)
    assert game.state.dice_mode == DiceMode.REALISTIC, "Dice mode should be REALISTIC"
    # Further assertions for realistic_roll could be added if min/max are known
    print(f"✓ Realistic dice roll (gear 3): {realistic_roll}")
    
    game.set_dice_mode(DiceMode.SIMPLE)
    simple_roll = game.roll_die(3)
    assert game.state.dice_mode == DiceMode.SIMPLE, "Dice mode should be SIMPLE"
    # Further assertions for simple_roll could be added if min/max are known
    print(f"✓ Simple dice roll (gear 3): {simple_roll}")
    
    print("\n✅ All tests passed! Game engine is working correctly.")
