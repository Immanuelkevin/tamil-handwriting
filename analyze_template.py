"""
Crop each box from temp sample.png and save as individual images
so we can visually inspect what character is in which position.
"""
from PIL import Image
import os, numpy as np

img = Image.open('temp sample.png').convert('RGB')
arr = np.array(img)

# The template appears to have ~6 columns and many rows
# Let's use the server.py constants to locate boxes
# From server.py: X_START=50, Y_START=50, BOX_SIZE=100, SPACING=50, COLS=6, ROW_GAP=50

X_START = 50
Y_START = 50
BOX_SIZE = 100
SPACING = 50
COLS = 6
ROW_GAP = 50

os.makedirs('template_boxes', exist_ok=True)

positions = []
x = X_START
y = Y_START
col = 0
box_num = 0

for i in range(270):  # up to 270 boxes
    positions.append((x, y, box_num))
    box_num += 1
    col += 1
    if col >= COLS:
        col = 0
        x = X_START
        y += BOX_SIZE + SPACING + ROW_GAP
    else:
        x += BOX_SIZE + SPACING

# Save first 30 boxes as images for inspection
for i, (bx, by, num) in enumerate(positions[:30]):
    crop = img.crop((bx, by, bx + BOX_SIZE, by + BOX_SIZE))
    crop = crop.resize((200, 200))
    crop.save(f'template_boxes/box_{i+1:03d}_x{bx}_y{by}.png')

print(f"Saved {min(30, len(positions))} box crops to template_boxes/")
print("First 30 positions:")
for i, (bx, by, num) in enumerate(positions[:30]):
    print(f"  Box {i+1:3d}: x={bx:4d}, y={by:4d}")
