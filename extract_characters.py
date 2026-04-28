from PIL import Image
import os
image = Image.open("filled_template_image.png")
characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
os.makedirs("character_images", exist_ok=True)
x = 50
y = 100
for char in characters:
    crop = image.crop((x, y, x+80, y+80))
    crop.save(f"character_images/{char}.png")
    x += 120
    if x > 2400:
        x = 50
        y += 150
print("Characters extracted")

