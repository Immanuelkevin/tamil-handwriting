import os
import fontforge
from PIL import Image, ImageDraw, ImageFont
font_size = 100
image_width = 2600
image_height = 1500
font_path = "arial.ttf"
template_image = "template_image.png"
filled_template = "filled_template_image.png"
output_folder = "character_images"
output_font = "handwritten_font.ttf"
characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
def create_template():
    img = Image.new("RGB",(image_width,image_height),"white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path,font_size)
    x = 50
    y = 50
    box_size = font_size
    positions = {}
    for ch in characters:
        draw.text((x,y),ch,fill="black",font=font)
        box = (x, y+120, x+box_size, y+120+box_size)
        draw.rectangle(box, outline="black")
        positions[ch] = box
        x += box_size * 2
        if x > image_width - box_size:
            x = 50
            y += box_size * 2
    img.save(template_image)
    print("Template image created:", template_image)
    return positions
def crop_letters(positions):
    img = Image.open(filled_template)
    os.makedirs(output_folder, exist_ok=True)
    for ch,pos in positions.items():
        crop = img.crop(pos)
        crop.save(os.path.join(output_folder,f"{ch}.png"))
    print("Characters extracted")
def create_font():
    font = fontforge.font()
    font.familyname = "MyHandwriting"
    font.fontname = "MyHandwriting"
    font.fullname = "MyHandwriting"
    for ch in characters:
        unicode_val = ord(ch)
        glyph = font.createChar(unicode_val)
        image_path = os.path.join(output_folder,f"{ch}.png")
        if os.path.exists(image_path):
            glyph.importOutlines(image_path)
            glyph.addExtrema()
            glyph.simplify()
            glyph.correctDirection()
            glyph.width = 1000
            print("Added glyph:",ch)
    font.generate(output_font)
    print("Font generated:",output_font)
def main():
    positions = create_template()
    print("")
    print("Open template_image.png")
    print("Write your handwriting in the boxes")
    print("Save it as filled_template_image.png")
    print("")
    input("Press ENTER after filling the template...")
    crop_letters(positions)
    create_font()
if __name__ == "__main__":
    main()
