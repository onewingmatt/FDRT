#!/usr/bin/env python3
"""
Simplified Track Coordinate Generator for Formula D
Creates realistic Monaco track coordinates without complex image processing
"""

import json
import math
from typing import List, Dict, Tuple

class MonacoTrackGenerator:
    def __init__(self):
        self.spaces = []
        
    def get_monaco_track_path(self):
        """Define the racing line through Monaco using key waypoints"""
        return [
            # Start/Finish straight
            (120, 580), (170, 580), (220, 580), (270, 580), (320, 580),
            
            # Sainte Devote corner entrance
            (360, 570), (380, 550), (390, 520), (395, 490), (390, 460),
            
            # Beau Rivage straight  
            (380, 430), (365, 410), (350, 395), (335, 385), (320, 380),
            (305, 375), (290, 370), (275, 365), (260, 360), (245, 355),
            
            # Massenet corner
            (230, 345), (215, 330), (200, 310), (185, 285), (170, 260),
            (155, 235), (140, 210), (130, 185), (125, 160), (125, 135),
            
            # Casino square
            (130, 110), (140, 90), (160, 75), (180, 65), (200, 60),
            (220, 58), (240, 58), (260, 60), (280, 65), (300, 75),
            
            # Grand Hotel Hairpin
            (310, 90), (315, 110), (318, 130), (320, 150), (318, 170),
            (315, 190), (310, 210), (305, 230), (295, 245), (280, 255),
            
            # Portier corner
            (265, 260), (250, 265), (235, 270), (220, 280), (205, 295),
            (190, 310), (175, 330), (160, 350), (145, 370), (130, 390),
            (115, 410), (100, 430), (85, 450), (70, 470), (55, 490),
            
            # Tunnel entrance
            (40, 510), (30, 530), (25, 550), (25, 570), (30, 590),
            (40, 610), (55, 630), (75, 645), (95, 655), (115, 660),
            
            # Swimming Pool chicane
            (135, 655), (155, 645), (175, 630), (195, 615), (215, 600),
            (235, 590), (255, 585), (275, 585), (295, 590), (310, 600),
            
            # Rascasse corner
            (320, 615), (330, 630), (335, 650), (335, 670), (330, 685),
            (320, 695), (305, 700), (285, 700), (265, 695), (245, 685),
            
            # Anthony Noghes to finish
            (225, 675), (205, 660), (185, 645), (165, 630), (145, 615),
            (125, 600), (110, 580), (105, 560), (105, 540), (110, 520),
            (115, 500), (120, 480), (125, 460), (130, 440), (135, 420),
        ]
    
    def get_section_info(self, space_id: int) -> Dict:
        """Get section information for a given space ID"""
        if space_id < 30:
            return {"name": "Start/Finish", "lanes": 3, "type": "straight"}
        elif space_id < 48:
            return {"name": "Sainte Devote", "lanes": 2, "type": "corner"}
        elif space_id < 72:
            return {"name": "Beau Rivage", "lanes": 3, "type": "straight"}
        elif space_id < 96:
            return {"name": "Massenet", "lanes": 3, "type": "corner"}
        elif space_id < 132:
            return {"name": "Casino", "lanes": 4, "type": "straight"}
        elif space_id < 162:
            return {"name": "Grand Hotel Hairpin", "lanes": 2, "type": "hairpin"}
        elif space_id < 207:
            return {"name": "Portier", "lanes": 3, "type": "corner"}
        elif space_id < 225:
            return {"name": "Tunnel", "lanes": 4, "type": "straight"}
        elif space_id < 243:
            return {"name": "Swimming Pool", "lanes": 2, "type": "chicane"}
        elif space_id < 258:
            return {"name": "Rascasse", "lanes": 2, "type": "corner"}
        elif space_id < 276:
            return {"name": "Anthony Noghes", "lanes": 3, "type": "corner"}
        else:
            return {"name": "Final", "lanes": 3, "type": "straight"}
    
    def get_corner_info(self, section_name: str) -> Dict:
        """Get corner stop requirements for a section"""
        corner_requirements = {
            "Sainte Devote": {"corner_zone": "sainte_devote", "stops_required": 1},
            "Massenet": {"corner_zone": "masgenet", "stops_required": 1},
            "Grand Hotel Hairpin": {"corner_zone": "hairpin", "stops_required": 2},
            "Portier": {"corner_zone": "portier", "stops_required": 1},
            "Swimming Pool": {"corner_zone": "pool", "stops_required": 1},
            "Rascasse": {"corner_zone": "rascasse", "stops_required": 1},
            "Anthony Noghes": {"corner_zone": "noghes", "stops_required": 1}
        }
        return corner_requirements.get(section_name, {"corner_zone": None, "stops_required": 0})
    
    def interpolate_path(self, path_points: List[Tuple[int, int]], num_points: int) -> List[Tuple[int, int]]:
        """Interpolate between path points to get smooth track"""
        if len(path_points) < 2:
            return path_points * num_points
        
        result = []
        for i in range(num_points):
            t = i / (num_points - 1)
            segment_length = len(path_points) - 1
            segment_index = int(t * segment_length)
            segment_t = (t * segment_length) % 1.0
            
            if segment_index >= len(path_points) - 1:
                x, y = path_points[-1]
            else:
                x1, y1 = path_points[segment_index]
                x2, y2 = path_points[segment_index + 1]
                x = x1 + (x2 - x1) * segment_t
                y = y1 + (y2 - y1) * segment_t
            
            result.append((int(x), int(y)))
        
        return result
    
    def calculate_track_angle(self, path_points: List[Tuple[int, int]], index: int) -> float:
        """Calculate the angle of the track at a given point"""
        if index >= len(path_points) - 1:
            return 0
        
        x1, y1 = path_points[index]
        x2, y2 = path_points[index + 1]
        
        return math.atan2(y2 - y1, x2 - x1)
    
    def generate_spaces(self):
        """Generate exactly 297 spaces for Monaco track"""
        track_path = self.get_monaco_track_path()
        
        # Interpolate path to get smooth points
        smooth_path = self.interpolate_path(track_path, 100)
        
        # Generate each space
        for space_id in range(297):
            section_info = self.get_section_info(space_id)
            corner_info = self.get_corner_info(section_info["name"])
            
            # Map space ID to position along track (0.0 to 1.0)
            track_position = space_id / 297.0
            path_index = int(track_position * len(smooth_path))
            path_index = min(path_index, len(smooth_path) - 1)
            
            base_x, base_y = smooth_path[path_index]
            
            # Calculate track angle for perpendicular lane offset
            track_angle = self.calculate_track_angle(smooth_path, path_index)
            
            # Perpendicular vector for lane positioning
            perp_x = -math.sin(track_angle)
            perp_y = math.cos(track_angle)
            
            # Determine lane for this space based on section and position
            lane_count = section_info["lanes"]
            lane = space_id % lane_count
            
            # Calculate lane offset (inside lane = 0)
            lane_spacing = 18
            lane_offset = (lane - (lane_count - 1) / 2) * lane_spacing
            
            # Final position
            x = base_x + perp_x * lane_offset
            y = base_y + perp_y * lane_offset
            
            space = {
                "id": space_id,
                "x": float(x),
                "y": float(y),
                "lane": lane,
                "total_lanes": lane_count,
                "section": section_info["name"],
                "space_type": corner_info["corner_zone"] and "corner" or "normal",
                "corner_zone": corner_info["corner_zone"],
                "corner_stops_required": corner_info["stops_required"],
                "connected_spaces": []
            }
            
            self.spaces.append(space)
        
        # Add connected spaces (simplified - each space connects to next in same lane)
        for i, space in enumerate(self.spaces):
            section_info = self.get_section_info(i)
            lane_count = section_info["lanes"]
            
            # Connect to next space in same lane
            next_space_id = i + lane_count
            if next_space_id < 297:
                space["connected_spaces"].append(next_space_id)
            
            # Connect to adjacent lanes (lane changing)
            if space["lane"] > 0:  # Can go to inside lane
                space["connected_spaces"].append(i - 1)
            if space["lane"] < lane_count - 1:  # Can go to outside lane
                space["connected_spaces"].append(i + 1)
    
    def save_coordinates(self, output_path: str):
        """Save coordinates to JSON file compatible with existing game system"""
        track_data = {
            "name": "Circuit de Monaco",
            "lap_length": 288,
            "start_positions": [0, 1, 2, 3, 4, 5, 6, 7],
            "corners": [
                {"name": "sainte_devote", "color": "blue", "stops_required": 1, "spaces": list(range(30, 48))},
                {"name": "masgenet", "color": "yellow", "stops_required": 1, "spaces": list(range(72, 96))},
                {"name": "hairpin", "color": "red", "stops_required": 2, "spaces": list(range(132, 162))},
                {"name": "portier", "color": "green", "stops_required": 1, "spaces": list(range(162, 207))},
                {"name": "pool", "color": "orange", "stops_required": 1, "spaces": list(range(225, 243))},
                {"name": "rascasse", "color": "purple", "stops_required": 1, "spaces": list(range(243, 258))},
                {"name": "noghes", "color": "cyan", "stops_required": 1, "spaces": list(range(258, 276))}
            ],
            "spaces": self.spaces
        }
        
        with open(output_path, 'w') as f:
            json.dump(track_data, f, indent=2)
        
        print(f"Generated {len(self.spaces)} spaces and saved to {output_path}")
        
        # Print some stats
        sections = {}
        for space in self.spaces:
            section = space["section"]
            if section not in sections:
                sections[section] = 0
            sections[section] += 1
        
        print(f"Spaces per section:")
        for section, count in sections.items():
            print(f"  {section}: {count} spaces")
    
    def generate(self, output_path: str = "monaco_track_coordinates.json"):
        """Main generation method"""
        print("Generating Monaco track coordinates...")
        self.generate_spaces()
        self.save_coordinates(output_path)
        return self.spaces

def main():
    generator = MonacoTrackGenerator()
    generator.generate()

if __name__ == "__main__":
    main()