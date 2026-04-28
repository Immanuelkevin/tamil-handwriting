from fontTools.ttLib import TTFont
import os

font_path = "output_font/TamilHandwritten.ttf"
if os.path.exists(font_path):
    font = TTFont(font_path)
    hmtx = font['hmtx']
    cmap = font.getBestCmap()
    
    # Check Pulli (்) - U+0BCD
    pulli_gid = cmap.get(0x0BCD)
    if pulli_gid:
        width = hmtx[pulli_gid][0]
        print(f"Pulli (0x0BCD) width: {width}")
    
    # Check Aa (ா) - U+0BBE
    aa_gid = cmap.get(0x0BBE)
    if aa_gid:
        width = hmtx[aa_gid][0]
        print(f"Sign Aa (0x0BBE) width: {width}")

    # Check Ka (க) - U+0B95
    ka_gid = cmap.get(0x0B95)
    if ka_gid:
        width = hmtx[ka_gid][0]
        print(f"Ka (0x0B95) width: {width}")
        
    font.close()
else:
    print(f"File not found: {font_path}")
