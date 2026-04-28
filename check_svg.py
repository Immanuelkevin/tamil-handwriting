import re
with open('output_font/font.svg', 'r', encoding='utf-8') as f:
    svg = f.read()
glyphs = re.findall(r'<glyph unicode="(.*?)" glyph-name="(.*?)" d="(.*?)"', svg)
empty = [name for char,name,d in glyphs if not d.strip() or 'M' not in d]
print(f'Total glyphs: {len(glyphs)}')
print(f'Empty/bad glyphs: {len(empty)} - {empty}')
if glyphs:
    print(f'First glyph d[:100]: {glyphs[0][2][:100]}')
