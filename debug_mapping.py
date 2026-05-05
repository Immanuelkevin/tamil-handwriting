"""
Generate a debug overlay: crop each box from temp sample.png,
draw the expected character from tamil_chars on it,
and save as a comparison image to spot mismatches.
"""
from PIL import Image, ImageDraw, ImageFont
import os, sys

sys.path.insert(0, '.')

# Read tamil_chars from server.py
tamil_chars = [
    'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',
    'ஃ',
    'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம',
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன',
    'க', 'கா', 'கி', 'கீ', 'கு', 'கூ', 'கெ', 'கே', 'கை', 'கொ', 'கோ', 'கௌ',
    'ங', 'ஙா', 'ஙி', 'ஙீ', 'ஙு', 'ஙூ', 'ஙெ', 'ஙே', 'ஙை', 'ஙொ', 'ஙோ', 'ஙௌ',
    'ச', 'சா', 'சி', 'சீ', 'சு', 'சூ', 'செ', 'சே', 'சை', 'சொ', 'சோ', 'சௌ',
    'ஞ', 'ஞா', 'ஞி', 'ஞீ', 'ஞு', 'ஞூ', 'ஞெ', 'ஞே', 'ஞை', 'ஞொ', 'ஞோ', 'ஞௌ',
    'ட', 'டா', 'டி', 'டீ', 'டு', 'டூ', 'டெ', 'டே', 'டை', 'டொ', 'டோ', 'டௌ',
    'ண', 'ணா', 'ணி', 'ணீ', 'ணு', 'ணூ', 'ணெ', 'ணே', 'ணை', 'ணொ', 'ணோ', 'ணௌ',
    'த', 'தா', 'தி', 'தீ', 'து', 'தூ', 'தெ', 'தே', 'தை', 'தொ', 'தோ', 'தௌ',
    'ந', 'நா', 'நி', 'நீ', 'நு', 'நூ', 'நெ', 'நே', 'நை', 'நொ', 'நோ', 'நௌ',
    'ப', 'பா', 'பி', 'பீ', 'பு', 'பூ', 'பெ', 'பே', 'பை', 'பொ', 'போ', 'பௌ',
    'ம', 'மா', 'மி', 'மீ', 'மு', 'மூ', 'மெ', 'மே', 'மை', 'மொ', 'மோ', 'மௌ',
    'ய', 'யா', 'யி', 'யீ', 'யு', 'யூ', 'யெ', 'யே', 'யை', 'யொ', 'யோ', 'யௌ',
    'ர', 'ரா', 'ரி', 'ரீ', 'ரு', 'ரூ', 'ரெ', 'ரே', 'ரை', 'ரொ', 'ரோ', 'ரௌ',
    'ல', 'லா', 'லி', 'லீ', 'லு', 'லூ', 'லெ', 'லே', 'லை', 'லொ', 'லோ', 'லௌ',
    'வ', 'வா', 'வி', 'வீ', 'வு', 'வூ', 'வெ', 'வே', 'வை', 'வொ', 'வோ', 'வௌ',
    'ழ', 'ழா', 'ழி', 'ழீ', 'ழு', 'ழூ', 'ழெ', 'ழே', 'ழை', 'ழொ', 'ழோ', 'ழௌ',
    'ள', 'ளா', 'ளி', 'ளீ', 'ளு', 'ளூ', 'ளெ', 'ளே', 'ளை', 'ளொ', 'ளோ', 'ளௌ',
    'ற', 'றா', 'றி', 'றீ', 'று', 'றூ', 'றெ', 'றே', 'றை', 'றொ', 'றோ', 'றௌ',
    'ன', 'னா', 'னி', 'னீ', 'னு', 'னூ', 'னெ', 'னே', 'னை', 'னொ', 'னோ', 'னௌ',
]

X_START = 50
Y_START = 50
BOX_SIZE = 100
SPACING = 50
COLS = 6
ROW_GAP = 50

img = Image.open('temp sample.png').convert('RGB')

# Build positions
positions = []
x, y, col = X_START, Y_START, 0
for i in range(len(tamil_chars)):
    positions.append((x, y))
    col += 1
    if col >= COLS:
        col = 0
        x = X_START
        y += BOX_SIZE + SPACING + ROW_GAP
    else:
        x += BOX_SIZE + SPACING

# Crop first 3 rows (18 boxes) from temp sample.png
ROWS_TO_SHOW = 3
height_to_crop = Y_START + ROWS_TO_SHOW * (BOX_SIZE + SPACING + ROW_GAP) + BOX_SIZE + 80
template_crop = img.crop((0, 0, 1000, height_to_crop))
draw = ImageDraw.Draw(template_crop)

try:
    font = ImageFont.truetype("C:\\Windows\\Fonts\\Nirmala.ttc", 14)
except:
    font = ImageFont.load_default()

# Draw expected char labels in RED on top of the template 
for i, (px, py) in enumerate(positions[:ROWS_TO_SHOW * COLS]):
    char = tamil_chars[i]
    # Draw red rectangle border
    draw.rectangle([px-2, py-2, px+BOX_SIZE+2, py+BOX_SIZE+2], outline='red', width=2)
    # Draw expected char number and character in red below the box
    draw.text((px, py + BOX_SIZE + 2), f"#{i+1}", fill='red', font=font)
    draw.text((px + 30, py + BOX_SIZE + 2), char, fill='blue', font=font)

template_crop.save('debug_mapping.png')
print(f"Saved debug_mapping.png")
print(f"First {ROWS_TO_SHOW * COLS} expected chars:")
for i in range(ROWS_TO_SHOW * COLS):
    print(f"  Box {i+1:3d} ({positions[i][0]:4d},{positions[i][1]:4d}): {tamil_chars[i]}")
