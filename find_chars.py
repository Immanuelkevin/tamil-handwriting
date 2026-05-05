from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

img = Image.open('temp sample.png').convert('L')
img_np = np.array(img)

# Fallback font
FONT_PATH = 'C:\\Windows\\Fonts\\latha.ttf'
if not os.path.exists(FONT_PATH):
    FONT_PATH = 'C:\\Windows\\Fonts\\Nirmala.ttc'

try:
    font = ImageFont.truetype(FONT_PATH, 40, index=0)
except:
    font = ImageFont.load_default()

candidates = list('0123456789.,!?;:\'\"-()[]') + list('ஶஜஷஸஹக்ஷ') + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + list('abcdefghijklmnopqrstuvwxyz') + list('௦௧௨௩௪௫௬௭௮௯௰௱௲')

def get_char_img(char):
    canvas = Image.new('L', (80, 60), 255)
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 10), char, fill=0, font=font)
    return np.array(canvas)

candidate_imgs = {c: get_char_img(c) for c in candidates}

x_start, y_start = 50, 50
box_size, spacing = 100, 50

# Check characters 247 to 270
x, y = x_start, y_start
for i in range(247):
    x += box_size + spacing
    if x > 1000 - box_size - spacing:
        x = x_start
        y += box_size + spacing + 50

found_chars = []
for i in range(247, 270):
    char_crop = img_np[y - 60 : y, x - 10 : x + 70]
    
    best_char = '?'
    best_mse = float('inf')
    for c, c_img in candidate_imgs.items():
        crop_pil = Image.fromarray(char_crop).resize((80, 60))
        mse = np.mean((np.array(crop_pil) - c_img)**2)
        if mse < best_mse:
            best_mse = mse
            best_char = c
            
    found_chars.append(best_char)
    x += box_size + spacing
    if x > 1000 - box_size - spacing:
        x = x_start
        y += box_size + spacing + 50

print('Extra characters:', ''.join(found_chars))
