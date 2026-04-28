from fontTools.ttLib import TTFont
import os

font_path = "output_font/TamilHandwritten.ttf"
if os.path.exists(font_path):
    font = TTFont(font_path)
    cmap = font['cmap'].getBestCmap()
    # Check for 'a' (97) and 'A' (65)
    has_a = 97 in cmap
    has_A = 65 in cmap
    print(f"Font at {font_path}")
    print(f"Contains 'a': {has_a}")
    print(f"Contains 'A': {has_A}")
    
    # Check some Tamil chars
    has_tamil = 2949 in cmap # அ (U+0B85)
    print(f"Contains Tamil 'அ': {has_tamil}")
    
    font.close()
else:
    print(f"File not found: {font_path}")
