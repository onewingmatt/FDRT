"""
Generate Monaco track with variable width (like real Formula D)
Each segment defines how many lanes are available
"""
import json
import math

# Monaco track definition with variable widths
MONACO_SEGMENTS = [
    # Format: (type, length_in_rows, lanes, name, corner_stops)
    ('straight', 10, 3, 'Start/Finish', 0),
    ('corner_tight', 6, 2, 'Sainte Devote', 1),  # TIGHT = 2 lanes
    ('straight', 8, 3, 'Beau Rivage', 0),
    ('corner_medium', 8, 3, 'Massenet', 2),
    ('straight', 12, 4, 'Casino Square', 0),  # WIDE = 4 lanes
    ('corner_tight', 10, 2, 'Grand Hotel Hairpin', 2),  # TIGHT = 2 lanes
    ('straight', 15, 3, 'Portier', 0),
    ('straight', 8, 4, 'Tunnel', 0),  # WIDE = 4 lanes
    ('corner_tight', 6, 2, 'Swimming Pool', 1),  # TIGHT = 2 lanes
    ('straight', 10, 3, 'After Pool', 0),
    ('corner_tight', 5, 2, 'Rascasse', 1),  # TIGHT = 2 lanes
    ('corner_medium', 6, 3, 'Anthony Noghes', 1),
    ('straight', 5, 3, 'Final Approach', 0),
]

spaces = []
space_id = 0
current_x = 100
current_y = 550
current_angle = 0  # Degrees

def add_segment(seg_type, rows, lanes, name, stops):
    global space_id, current_x, current_y, current_angle
    
    print(f"Adding {name}: {rows} rows × {lanes} lanes = {rows * lanes} spaces")
    
    if 'straight' in seg_type:
        # Straight section
        for row in range(rows):
            for lane in range(lanes):
                # Calculate position
                dx = math.cos(math.radians(current_angle))
                dy = math.sin(math.radians(current_angle))
                
                # Lane offset (perpendicular to direction)
                lane_width = 18
                lane_offset = (lane - (lanes-1)/2) * lane_width
                perp_x = -math.sin(math.radians(current_angle)) * lane_offset
                perp_y = math.cos(math.radians(current_angle)) * lane_offset
                
                x = current_x + row * 20 * dx + perp_x
                y = current_y + row * 20 * dy + perp_y
                
                spaces.append({
                    'id': space_id,
                    'x': round(x, 1),
                    'y': round(y, 1),
                    'lane': lane,
                    'total_lanes': lanes,
                    'section': name,
                    'corner_stops': stops
                })
                space_id += 1
        
        # Move current position
        current_x += rows * 20 * math.cos(math.radians(current_angle))
        current_y += rows * 20 * math.sin(math.radians(current_angle))
    
    elif 'corner' in seg_type:
        # Corner section
        if 'tight' in seg_type:
            turn_angle = 90
            radius = 60
        else:
            turn_angle = 60
            radius = 80
        
        # Determine turn direction from context
        turn_direction = 1  # Will alternate or be set by track logic
        
        for row in range(rows):
            progress = row / rows
            angle = current_angle + turn_direction * turn_angle * progress
            
            for lane in range(lanes):
                lane_width = 18
                r = radius + (lane - (lanes-1)/2) * lane_width
                
                # Calculate center of turn
                perp_angle = current_angle + turn_direction * 90
                cx = current_x + radius * math.cos(math.radians(perp_angle))
                cy = current_y + radius * math.sin(math.radians(perp_angle))
                
                # Position on arc
                arc_angle = current_angle - turn_direction * 90 + turn_direction * turn_angle * progress
                x = cx + r * math.cos(math.radians(arc_angle))
                y = cy + r * math.sin(math.radians(arc_angle))
                
                spaces.append({
                    'id': space_id,
                    'x': round(x, 1),
                    'y': round(y, 1),
                    'lane': lane,
                    'total_lanes': lanes,
                    'section': name,
                    'corner_stops': stops
                })
                space_id += 1
        
        # Update angle and position
        current_angle += turn_direction * turn_angle
        current_x = cx + radius * math.cos(math.radians(current_angle - turn_direction * 90))
        current_y = cy + radius * math.sin(math.radians(current_angle - turn_direction * 90))

# Generate track
for segment in MONACO_SEGMENTS:
    add_segment(*segment)

print(f"\n✅ Generated {space_id} total spaces")
print(f"   Total rows: {sum(s[1] for s in MONACO_SEGMENTS)}")

# Save
with open('monaco_variable_width.json', 'w') as f:
    json.dump(spaces, f, indent=2)

print("✅ Saved to monaco_variable_width.json")
