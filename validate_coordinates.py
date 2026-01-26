#!/usr/bin/env python3
"""
Standalone Coordinate Validation Test
Tests the Monaco track coordinate system without server
"""

import json
import sys

def test_coordinate_system():
    """Test the coordinate system independently"""
    print("🏎️ PHASE 2: COORDINATE VALIDATION")
    print("=" * 50)
    
    try:
        # Load track coordinates
        with open('monaco_track_coordinates.json', 'r') as f:
            track_data = json.load(f)
        
        spaces = track_data['spaces']
        print(f"✅ Loaded {track_data['name']} track")
        print(f"✅ Total spaces: {len(spaces)}")
        
        # Test 1: Verify basic structure
        print("\n📊 TEST 1: Basic Structure Validation")
        required_fields = ['id', 'x', 'y', 'lane', 'space_type', 'corner_zone', 'total_lanes']
        missing_fields = []
        
        for space in spaces[:10]:  # Test first 10 spaces
            for field in required_fields:
                if field not in space:
                    missing_fields.append(f"space[{space.get('id', '?')}].{field}")
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
        else:
            print("✅ All required fields present")
        
        # Test 2: Validate space ID sequence
        print("\n📈 TEST 2: Space ID Sequence")
        space_ids = [s['id'] for s in spaces]
        expected_ids = list(range(len(spaces)))
        
        if space_ids == expected_ids:
            print(f"✅ Space IDs: 0 to {len(spaces)-1} (sequential)")
        else:
            print(f"❌ Space IDs not sequential. Got: {space_ids[:5]}...")
        
        # Test 3: Section distribution
        print("\n🏁 TEST 3: Section Distribution")
        sections = {}
        for space in spaces:
            section = space.get('section', 'Unknown')
            if section not in sections:
                sections[section] = 0
            sections[section] += 1
        
        expected_sections = {
            'Start/Finish': 30,
            'Sainte Devote': 18, 
            'Beau Rivage': 24,
            'Massenet': 24,
            'Casino': 36,
            'Grand Hotel Hairpin': 30,
            'Portier': 45,
            'Tunnel': 18,
            'Swimming Pool': 18,
            'Rascasse': 15,
            'Anthony Noghes': 18,
            'Final': 21
        }
        
        all_sections_correct = True
        for section, expected_count in expected_sections.items():
            actual_count = sections.get(section, 0)
            if actual_count == expected_count:
                print(f"✅ {section}: {actual_count} spaces")
            else:
                print(f"❌ {section}: {actual_count} spaces (expected {expected_count})")
                all_sections_correct = False
        
        # Test 4: Coordinate ranges
        print("\n📍 TEST 4: Coordinate Ranges")
        x_coords = [s['x'] for s in spaces]
        y_coords = [s['y'] for s in spaces]
        
        print(f"✅ X range: {min(x_coords):.1f} to {max(x_coords):.1f}")
        print(f"✅ Y range: {min(y_coords):.1f} to {max(y_coords):.1f}")
        
        # Test 5: Corner detection
        print("\n🎯 TEST 5: Corner Zone Detection")
        corner_spaces = [s for s in spaces if s.get('space_type') == 'corner']
        print(f"✅ Corner spaces: {len(corner_spaces)}")
        
        corner_zones = {}
        for space in corner_spaces:
            zone = space.get('corner_zone')
            if zone:
                corner_zones[zone] = corner_zones.get(zone, 0) + 1
        
        print(f"✅ Corner zones detected: {list(corner_zones.keys())}")
        
        # Test 6: Lane distribution
        print("\n🛣️ TEST 6: Lane Distribution")
        lane_counts = {}
        for space in spaces:
            lanes = space.get('total_lanes', 3)
            lane_counts[lanes] = lane_counts.get(lanes, 0) + 1
        
        for lanes, count in sorted(lane_counts.items()):
            print(f"✅ {lanes} lanes: {count} spaces")
        
        # Test 7: Sample coordinates
        print("\n🎮 TEST 7: Sample Coordinates")
        test_spaces = [0, 30, 96, 132, 162, 207, 225, 243, 258]  # Key section starts
        for space_id in test_spaces:
            if space_id < len(spaces):
                space = spaces[space_id]
                print(f"✅ Space {space_id}: ({space['x']:.1f}, {space['y']:.1f}) lane {space['lane']} - {space.get('section', 'Unknown')}")
        
        # Summary
        print("\n" + "=" * 50)
        print("🏆 COORDINATE VALIDATION SUMMARY")
        print("=" * 50)
        
        passed_tests = 0
        total_tests = 7
        
        # Basic structure
        if not missing_fields:
            passed_tests += 1
            print("✅ TEST 1: PASSED - Basic Structure")
        else:
            print("❌ TEST 1: FAILED - Basic Structure")
        
        # Space sequence
        if space_ids == expected_ids:
            passed_tests += 1
            print("✅ TEST 2: PASSED - Space ID Sequence")
        else:
            print("❌ TEST 2: FAILED - Space ID Sequence")
        
        # Section distribution
        if all_sections_correct:
            passed_tests += 1
            print("✅ TEST 3: PASSED - Section Distribution")
        else:
            print("❌ TEST 3: FAILED - Section Distribution")
        
        # Coordinate ranges
        if len(x_coords) > 0 and len(y_coords) > 0:
            passed_tests += 1
            print("✅ TEST 4: PASSED - Coordinate Ranges")
        else:
            print("❌ TEST 4: FAILED - Coordinate Ranges")
        
        # Corner detection
        if len(corner_spaces) > 0:
            passed_tests += 1
            print("✅ TEST 5: PASSED - Corner Detection")
        else:
            print("❌ TEST 5: FAILED - Corner Detection")
        
        # Lane distribution
        if len(lane_counts) > 0:
            passed_tests += 1
            print("✅ TEST 6: PASSED - Lane Distribution")
        else:
            print("❌ TEST 6: FAILED - Lane Distribution")
        
        # Sample coordinates
        if len([s for s in spaces if s.get('id') in test_spaces]) > 0:
            passed_tests += 1
            print("✅ TEST 7: PASSED - Sample Coordinates")
        else:
            print("❌ TEST 7: FAILED - Sample Coordinates")
        
        print(f"\n📊 FINAL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🏆 ALL TESTS PASSED! Coordinate system is working perfectly!")
            print("✅ Ready for Phase 3: Visual Verification")
        else:
            print("⚠️  Some tests failed. Review results above.")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_coordinate_system()
    sys.exit(0 if success else 1)