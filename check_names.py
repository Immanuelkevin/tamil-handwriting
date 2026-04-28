from fontTools.ttLib import TTFont
import os

font_path = "output_font/TamilHandwritten.ttf"
if os.path.exists(font_path):
    font = TTFont(font_path)
    print("Name Table Entries:")
    for record in font['name'].names:
        try:
            name_str = record.toUnicode()
            print(f"ID {record.nameID}: {name_str}")
        except:
            pass
    font.close()
else:
    print(f"File not found: {font_path}")
