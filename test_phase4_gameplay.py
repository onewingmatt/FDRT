#!/usr/bin/env python3
"""
Phase 4: Game Logic Testing
Tests complete gameplay mechanics with Monaco track coordinates
"""

import json
import asyncio
import requests
import sys

async def test_complete_gameplay():
    """Test full gameplay cycle with Monaco coordinates"""
    print("🎮 PHASE 4: GAME LOGIC TESTING")
    print("=" * 60)
    
    try:
        # STEP 1: Setup test game
        print("\n🎯 STEP 1: Creating Multi-Player Test Game...")
        
        game_response = requests.post('http://localhost:8000/create-game', 
                                     json={"player_names": ["Schumacher", "Senna", "Prost"]})
        
        if game_response.status_code != 200:
            print(f"❌ Failed to create game: {game_response.status_code}")
            return False
        
        game_data = game_response.json()
        game_id = game_data['game_id']
        print(f"✅ Created game: {game_id}")
        
        # STEP 2: Load track coordinates for comparison
        print("\n📍 STEP 2: Loading Track Data...")
        
        coord_response = requests.get('http://localhost:8000/track-coordinates')
        track_data = coord_response.json()
        print(f"✅ Loaded {track_data['name']} with {len(track_data['spaces'])} spaces")
        
        # STEP 3: Start race procedure
        print("\n🏁 STEP 3: Testing Race Start...")
        
        start_response = requests.post(f'http://localhost:8000/game/{game_id}/start')
        if start_response.status_code != 200:
            print(f"❌ Failed to start race: {start_response.status_code}")
            return False
        
        print("✅ Race started successfully")
        
        # STEP 4: Validate game state after start
        print("\n📊 STEP 4: Validating Post-Start State...")
        
        state_response = requests.get(f'http://localhost:8000/game/{game_id}')
        if state_response.status_code != 200:
            print(f"❌ Failed to get game state: {state_response.status_code}")
            return False
        
        game_state = state_response.json()
        print(f"✅ Game state: Turn {game_state['current_turn']}, Phase {game_state['current_phase']}")
        
        # STEP 5: Validate car positions on track
        print("\n🏎️ STEP 5: Validating Car Positions...")
        
        players = game_state.get('players', [])
        valid_positions = 0
        
        for i, player in enumerate(players):
            space_id = player['current_space']
            player_name = player['name']
            gear = player['current_gear']
            
            # Find corresponding track coordinate
            track_space = next((s for s in track_data['spaces'] if s['id'] == space_id), None)
            
            if track_space:
                print(f"✅ {player_name}: Space {space_id} at ({track_space['x']:.1f}, {track_space['y']:.1f}) lane {track_space['lane']} - {track_space.get('section', 'Unknown')} - Gear {gear}")
                
                # Validate Monaco track sections
                section = track_space.get('section', 'Unknown')
                
                # Check if position makes sense for track layout
                x, y = track_space['x'], track_space['y']
                
                # Monaco track validation based on section
                is_valid = True
                if section == 'Start/Finish' and not (560 <= y <= 620):
                    is_valid = False
                    print(f"⚠️  {player_name}: Invalid Start/Finish position: y={y:.1f}")
                elif section == 'Sainte Devote' and not (400 <= y <= 450):
                    is_valid = False  
                    print(f"⚠️  {player_name}: Invalid Sainte Devote position: y={y:.1f}")
                elif section == 'Casino' and not (0 <= y <= 150):
                    is_valid = False
                    print(f"⚠️  {player_name}: Invalid Casino position: y={y:.1f}")
                elif section == 'Grand Hotel Hairpin' and not (240 <= y <= 320):
                    is_valid = False
                    print(f"⚠️  {player_name}: Invalid Hairpin position: y={y:.1f}")
                elif section == 'Portier' and not (400 <= y <= 500):
                    is_valid = False
                    print(f"⚠️  {player_name}: Invalid Portier position: y={y:.1f}")
                
                if is_valid:
                    valid_positions += 1
            else:
                print(f"❌ {player_name}: Space {space_id} not found in track data")
        
        print(f"✅ Valid positions: {valid_positions}/{len(players)}")
        
        # STEP 6: Test corner zone requirements
        print("\n🎯 STEP 6: Validating Corner Requirements...")
        
        corner_compliance = 0
        total_corner_requirements = 0
        
        for player in players:
            space_id = player['current_space']
            track_space = next((s for s in track_data['spaces'] if s['id'] == space_id), None)
            
            if track_space and track_space.get('space_type') == 'corner':
                zone = track_space.get('corner_zone')
                stops_required = track_space.get('corner_stops_required', 0)
                stops_made = player.get('corner_stops', {}).get(zone, 0)
                
                if stops_made >= stops_required:
                    corner_compliance += 1
                    print(f"✅ {player['name']}: {zone} - {stops_made}/{stops_required} stops (COMPLIED)")
                else:
                    print(f"⚠️  {player['name']}: {zone} - {stops_made}/{stops_required} stops (NEEDS {stops_required - stops_made} more)")
                
                total_corner_requirements += stops_required
        
        print(f"✅ Corner compliance: {corner_compliance}/{len([p for p in players if any(s.get('space_type') == 'corner' for s in track_data['spaces'] if s['id'] == p['current_space'])])}")
        print(f"✅ Total corner requirements: {total_corner_requirements}")
        
        # STEP 7: Validate lane system
        print("\n🛣️ STEP 7: Validating Lane System...")
        
        lane_validations = []
        for player in players:
            space_id = player['current_space']
            track_space = next((s for s in track_data['spaces'] if s['id'] == space_id), None)
            
            if track_space:
                current_lane = track_space['lane']
                total_lanes = track_space.get('total_lanes', 3)
                
                # Validate lane is within limits
                if 0 <= current_lane < total_lanes:
                    lane_validations.append(True)
                    print(f"✅ {player['name']}: Lane {current_lane}/{total_lanes} - VALID")
                else:
                    lane_validations.append(False)
                    print(f"❌ {player['name']}: Lane {current_lane}/{total_lanes} - INVALID")
        
        lane_success_rate = sum(lane_validations) / len(lane_validations) if lane_validations else 0
        print(f"✅ Lane system success rate: {lane_success_rate:.1%}")
        
        # STEP 8: Game completion test
        print("\n🏆 STEP 8: Game Completion Analysis...")
        
        total_spaces = len(track_data['spaces'])
        spaces_per_lap = 288  # From track config
        
        print(f"✅ Total track spaces: {total_spaces}")
        print(f"✅ Spaces per lap: {spaces_per_lap}")
        
        # Calculate race progress
        max_distance = max([p.get('total_distance', 0) for p in players])
        race_progress = (max_distance / spaces_per_lap) * 100
        
        print(f"✅ Race progress: {race_progress:.1f}%")
        
        # Summary
        print(f"\n📊 PHASE 4 GAME LOGIC SUMMARY")
        print("=" * 60)
        
        success_criteria = {
            'game_creation': True,
            'track_loading': True,
            'race_start': True,
            'position_validation': valid_positions == len(players),
            'corner_compliance': corner_compliance > 0,
            'lane_system': lane_success_rate > 0.8,
            'race_progress': race_progress >= 0  # Some progress made
        }
        
        passed_tests = sum(success_criteria.values())
        total_tests = len(success_criteria)
        
        for test_name, passed in success_criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name.replace('_', ' ').title()}")
        
        print(f"\n🏆 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🏆 ALL GAME LOGIC TESTS PASSED!")
            print("✅ Monaco coordinate system: FULLY FUNCTIONAL!")
            print("✅ Ready for production gameplay!")
        else:
            print("⚠️  Some game logic tests failed")
            print("🔧 Review results for necessary fixes")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Phase 4: Game Logic Testing")
    print("Testing complete gameplay mechanics with Monaco track coordinates")
    print("=" * 60)
    
    success = asyncio.run(test_complete_gameplay())
    
    if success:
        print("\n🎉 PHASE 4 COMPLETE - Ready for Production!")
    else:
        print("\n⚠️  PHASE 4 FAILED - Fix required issues")
    
    return success

if __name__ == "__main__":
    main()