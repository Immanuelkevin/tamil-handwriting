import os
import fontforge
image_folder = "character_images"
output_font = "handwritten_font.ttf"
characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
font = fontforge.font()
font.familyname = "MyHandwriting"
font.fontname = "MyHandwriting"
font.fullname = "MyHandwriting"
for ch in characters:
    unicode_value = ord(ch)
    glyph = font.createChar(unicode_value)
    image_path = os.path.join(image_folder, f"{ch}.png")
    if os.path.exists(image_path):
        print("Adding glyph:", ch)
        glyph.importOutlines(image_path)
        glyph.addExtrema()
        glyph.simplify()
        glyph.correctDirection()
        glyph.width = 1000
font.generate(output_font)
print("Font created:", output_font)
