import fontforge
font = fontforge.font()
font.fontname = "HandwritingFont"
font.familyname = "HandwritingFont"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for ch in letters:
    glyph = font.createChar(ord(ch))
    glyph.importOutlines("letters.svg")
    glyph.width = 1000
font.generate("handwriting.ttf")
print("Font generated")
