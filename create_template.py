from PIL import Image, ImageDraw, ImageFont
font_size = 80
image_width = 2600
image_height = 1200
font_path = "arial.ttf"
output_image_path = "template_image.png"
characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
template_image = Image.new("RGB", (image_width, image_height), "white")
draw = ImageDraw.Draw(template_image)
font = ImageFont.truetype(font_path, font_size)
x = 50
y = 100
character_positions = {}
for char in characters:
    draw.text((x, y-60), char, fill="black", font=font)
    draw.rectangle([x, y, x+80, y+80], outline="black")
    character_positions[char] = (x, y, x+80, y+80)
    x += 120
    if x > 2400:
        x = 50
        y += 150
template_image.save(output_image_path)
print("Template created:", output_image_path)

