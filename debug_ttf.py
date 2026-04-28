from fontTools.ttLib import TTFont

t = TTFont('output_font/TamilPython.ttf')
glyf = t['glyf']

glyph_order = t.getGlyphOrder()
for name in glyph_order[:5]:
    g = glyf[name]
    nc = getattr(g, 'numberOfContours', 'N/A')
    print(f'{name}: numberOfContours={nc}')
