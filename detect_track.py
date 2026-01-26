import cv2
import numpy as np
import json
from PIL import Image

# Load the board image
img = cv2.imread('monaco_board.jpg')
print(f"Image size: {img.shape[1]}x{img.shape[0]}")

# Convert to HSV for better color detection
hsv = img.copy()

# Create a simple interactive tool
positions = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        positions.append({"x": x, "y": y})
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.putText(img, str(len(positions)), (x+10, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.imshow('Track Builder - Click spaces in order, Q to quit', img)
        print(f"Position {len(positions)}: [{x}, {y}]")

# Show image
cv2.namedWindow('Track Builder - Click spaces in order, Q to quit')
cv2.setMouseCallback('Track Builder - Click spaces in order, Q to quit', click_event)
cv2.imshow('Track Builder - Click spaces in order, Q to quit', img)

print("Click on each track space in racing order. Press 'Q' when done, 'S' to save.")

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        with open('track_positions.json', 'w') as f:
            json.dump(positions, f, indent=2)
        print(f"Saved {len(positions)} positions!")

cv2.destroyAllWindows()
print(f"\nTotal positions: {len(positions)}")
