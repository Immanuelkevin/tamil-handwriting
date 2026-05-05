import re
with open('output_font/font.svg', 'r', encoding='utf-8') as f:
    svg_text = f.read()

glyphs_data = re.findall(r'<glyph unicode="(.*?)" glyph-name="(.*?)" d="(.*?)" horiz-adv-x="(.*?)"', svg_text)

char_to_glyph = {}
for g in glyphs_data:
    if len(g[0]) == 1:
        char_to_glyph[g[0]] = g[1]

fea_text = 'languagesystem DFLT dflt;\nlanguagesystem taml dflt;\nlanguagesystem tml2 dflt;\n\n'
fea_text += 'feature ccmp {\n'
count = 0
for g in glyphs_data:
    if len(g[0]) > 1:
        seq = []
        for c in g[0]:
            if c in char_to_glyph:
                seq.append(char_to_glyph[c])
            else:
                seq = None
                break
        if seq:
            fea_text += f'    sub {" ".join(seq)} by {g[1]};\n'
            count += 1
fea_text += '} ccmp;\n'
print("Generated ligatures:", count)
