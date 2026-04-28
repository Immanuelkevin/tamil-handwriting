import os
import unicodedata
import shutil
import subprocess
import datetime
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from bson.binary import Binary
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from db import get_db_connection
except ImportError:
    get_db_connection = None

app = FastAPI()

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

tamil_chars = [
    # ── SECTION 1: Pure Vowels / Uyir (12) ──
    'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',

    # ── SECTION 2: Aytham (1) ──
    'ஃ',

    # ── SECTION 3: Pure Consonants / Mei (18) ──
    'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம',
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன',

    # ── SECTION 4: Uyirmei (18 consonants × 12 vowels = 216) ──
    # Each row: [a, aa, i, ii, u, uu, e, ee, ai, o, oo, au]

    # க row
    'க', 'கா', 'கி', 'கீ', 'கு', 'கூ', 'கெ', 'கே', 'கை', 'கொ', 'கோ', 'கௌ',
    # ங row
    'ங', 'ஙா', 'ஙி', 'ஙீ', 'ஙு', 'ஙூ', 'ஙெ', 'ஙே', 'ஙை', 'ஙொ', 'ஙோ', 'ஙௌ',
    # ச row
    'ச', 'சா', 'சி', 'சீ', 'சு', 'சூ', 'செ', 'சே', 'சை', 'சொ', 'சோ', 'சௌ',
    # ஞ row
    'ஞ', 'ஞா', 'ஞி', 'ஞீ', 'ஞு', 'ஞூ', 'ஞெ', 'ஞே', 'ஞை', 'ஞொ', 'ஞோ', 'ஞௌ',
    # ட row
    'ட', 'டா', 'டி', 'டீ', 'டு', 'டூ', 'டெ', 'டே', 'டை', 'டொ', 'டோ', 'டௌ',
    # ண row
    'ண', 'ணா', 'ணி', 'ணீ', 'ணு', 'ணூ', 'ணெ', 'ணே', 'ணை', 'ணொ', 'ணோ', 'ணௌ',
    # த row
    'த', 'தா', 'தி', 'தீ', 'து', 'தூ', 'தெ', 'தே', 'தை', 'தொ', 'தோ', 'தௌ',
    # ந row
    'ந', 'நா', 'நி', 'நீ', 'நு', 'நூ', 'நெ', 'நே', 'நை', 'நொ', 'நோ', 'நௌ',
    # ப row
    'ப', 'பா', 'பி', 'பீ', 'பு', 'பூ', 'பெ', 'பே', 'பை', 'பொ', 'போ', 'பௌ',
    # ம row
    'ம', 'மா', 'மி', 'மீ', 'மு', 'மூ', 'மெ', 'மே', 'மை', 'மொ', 'மோ', 'மௌ',
    # ய row
    'ய', 'யா', 'யி', 'யீ', 'யு', 'யூ', 'யெ', 'யே', 'யை', 'யொ', 'யோ', 'யௌ',
    # ர row
    'ர', 'ரா', 'ரி', 'ரீ', 'ரு', 'ரூ', 'ரெ', 'ரே', 'ரை', 'ரொ', 'ரோ', 'ரௌ',
    # ல row
    'ல', 'லா', 'லி', 'லீ', 'லு', 'லூ', 'லெ', 'லே', 'லை', 'லொ', 'லோ', 'லௌ',
    # வ row
    'வ', 'வா', 'வி', 'வீ', 'வு', 'வூ', 'வெ', 'வே', 'வை', 'வொ', 'வோ', 'வௌ',
    # ழ row
    'ழ', 'ழா', 'ழி', 'ழீ', 'ழு', 'ழூ', 'ழெ', 'ழே', 'ழை', 'ழொ', 'ழோ', 'ழௌ',
    # ள row
    'ள', 'ளா', 'ளி', 'ளீ', 'ளு', 'ளூ', 'ளெ', 'ளே', 'ளை', 'ளொ', 'ளோ', 'ளௌ',
    # ற row
    'ற', 'றா', 'றி', 'றீ', 'று', 'றூ', 'றெ', 'றே', 'றை', 'றொ', 'றோ', 'றௌ',
    # ன row
    'ன', 'னா', 'னி', 'னீ', 'னு', 'னூ', 'னெ', 'னே', 'னை', 'னொ', 'னோ', 'னௌ',
]

# Prefer local Tamil font if present (crucial for Linux servers like Render)
if os.path.exists("Tamil.ttf"):
    FONT_PATH = "Tamil.ttf"
elif os.path.exists("C:\\Windows\\Fonts\\latha.ttf"):
    FONT_PATH = "C:\\Windows\\Fonts\\latha.ttf"
elif os.path.exists("C:\\Windows\\Fonts\\Nirmala.ttc"):
    FONT_PATH = "C:\\Windows\\Fonts\\Nirmala.ttc"
else:
    FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"

def create_template_image(output_path, chars_to_use=None):
    if chars_to_use is None:
        chars_to_use = tamil_chars
        
    font_size = 40
    image_width = 1000
    rows = (len(chars_to_use) + 5) // 6
    image_height = rows * 200 + 100
    template_image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(template_image)
    try:
        # index=0 ensures first face is loaded from .ttc collections
        font = ImageFont.truetype(FONT_PATH, font_size, index=0)
        font_small = ImageFont.truetype(FONT_PATH, 18, index=0)
    except IOError:
        font = ImageFont.load_default()
        font_small = font

    x_start = 50
    y_start = 50
    box_size = 100
    spacing = 50
    
    x, y = x_start, y_start
    positions = {}

    for idx, char in enumerate(chars_to_use, start=1):
        # NFC normalization ensures split vowels (ொ ோ ௌ) are in precomposed form
        display_char = unicodedata.normalize('NFC', char)
        # Draw box number (small, top-left corner)
        draw.text((x + 4, y + 4), str(idx), fill="#aaaaaa", font=font_small)
        # Draw the Tamil character label above the box
        draw.text((x + 20, y - font_size - 8), display_char, fill="black", font=font)
        box_coords = (x, y, x + box_size, y + box_size)
        # Use light grey so the cv2 threshold of 150 completely ignores the border!
        draw.rectangle(box_coords, outline="#e0e0e0")
        positions[char] = box_coords
        
        x += box_size + spacing
        if x > image_width - box_size - spacing:
            x = x_start
            y += box_size + spacing + 50

    template_image.save(output_path)
    return positions

def extract_and_vectorize(filled_image_path, positions):
    from itertools import cycle
    img = Image.open(filled_image_path)
    
    image_width = 1000
    
    if img.width != image_width:
        aspect_ratio = img.height / img.width
        img = img.resize((image_width, int(image_width * aspect_ratio)))
        
    os.makedirs("extracted_images", exist_ok=True)
    os.makedirs("output_font", exist_ok=True)
    
    extracted_paths = {}
    
    svg_font_content = f"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >
<svg xmlns="http://www.w3.org/2000/svg">
<defs>
  <font id="TamilHand-Final" horiz-adv-x="1000">
    <font-face font-family="TamilHand-Final" units-per-em="1000" ascent="1000" descent="0" />
    <missing-glyph horiz-adv-x="1000" />
"""
    
    for char, pos in positions.items():
        pad = 5
        clean_pos = (pos[0] + pad, pos[1] + pad, pos[2] - pad, pos[3] - pad)
        crop = img.crop(clean_pos)
        
        char_hex = "_".join([hex(ord(c))[2:].upper() for c in char])
        char_name = f"uni{char_hex}"
        png_path = f"extracted_images/{char_name}.png"
        crop.save(png_path)
        
        cv_img = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
        # Use 140 instead of 200 to make the lines look thinner and more natural
        _, thresh = cv2.threshold(cv_img, 140, 255, cv2.THRESH_BINARY_INV)
        
        # Erase the outer 2 pixels strictly to prevent border bleed
        thresh[0:2, :] = 0
        thresh[-2:, :] = 0
        thresh[:, 0:2] = 0
        thresh[:, -2:] = 0
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        h, w = cv_img.shape
        scale_x = 1000.0 / w
        scale_y = 1000.0 / h
        
        d_all = ""
        for cnt in contours:
            if len(cnt) > 2:
                # The ultimate geometric grid box mathematically infallible filter!
                # If a shape is practically a perfect square/rectangle, its extent is ~0.95+
                # Handwriting (even circles) naturally hits ~0.75 max
                x_b, y_b, w_b, h_b = cv2.boundingRect(cnt)
                rect_area = w_b * h_b
                if rect_area > 0:
                    extent = cv2.contourArea(cnt) / rect_area
                    if extent > 0.85 and w_b > 20 and h_b > 20:
                        continue # Perfect geometric box erased!
                    
                pts = cnt.reshape(-1, 2)
                start_x = int(pts[0][0] * scale_x)
                start_y = int(1000 - (pts[0][1] * scale_y)) # Use 1000 for full em
                d_all += f"M{start_x} {start_y} "
                
                for pt in pts[1:]:
                    pt_x = int(pt[0] * scale_x)
                    pt_y = int(1000 - (pt[1] * scale_y))
                    d_all += f"L{pt_x} {pt_y} "
                d_all += "Z "
                
        svg_font_content += f'    <glyph unicode="{char}" glyph-name="{char_name}" d="{d_all.strip()}" horiz-adv-x="1000" />\n'
        extracted_paths[char] = d_all.strip()
        
    synthesized_marks = [
        # format: (unicode_char, glyph_name, path, advance_width)
        ("்", "uni0BCD", "M -550 700 C -600 700, -600 800, -550 800 C -500 800, -500 700, -550 700 Z", 0),
        ("ா", "uni0BBE", extracted_paths.get('ர', ''), 1000),
        ("ி", "uni0BBF", "M -200 600 C -200 1000, -700 1000, -700 600 L -600 600 C -600 850, -300 850, -300 600 Z", 0),
        ("ீ", "uni0BC0", "M -200 600 C -200 1000, -700 1000, -700 600 L -600 600 C -600 850, -300 850, -300 600 Z M -400 850 C -500 850, -500 1000, -400 1000 C -300 1000, -300 850, -400 850 Z", 0),
        ("ு", "uni0BC1", "M -300 0 C -300 -400, -800 -400, -800 -100 L -700 -100 C -700 -300, -400 -300, -400 0 Z", 0),
        ("ூ", "uni0BC2", "M -300 0 C -300 -400, -800 -400, -800 -100 L -700 -100 C -700 -300, -400 -300, -400 0 Z M -400 -100 C -500 -100, -500 -300, -400 -300 C -300 -300, -300 -100, -400 -100 Z", 0),
        ("ெ", "uni0BC6", "M 300 100 C 200 100, 200 400, 300 400 C 400 400, 400 700, 300 700 C 200 700, 200 500, 300 500 L 300 600 C 250 600, 250 650, 300 650 C 350 650, 350 450, 300 450 C 250 450, 250 150, 300 150 Z", 1000),
        ("ே", "uni0BC7", "M 300 100 C 200 100, 200 400, 300 400 C 400 400, 400 700, 300 700 C 200 700, 200 500, 300 500 L 300 600 C 250 600, 250 650, 300 650 C 350 650, 350 450, 300 450 C 250 450, 250 150, 300 150 Z M 500 100 C 400 100, 400 400, 500 400 C 600 400, 600 700, 500 700 C 400 700, 400 500, 500 500 L 500 600 C 450 600, 450 650, 500 650 C 550 650, 550 450, 500 450 C 450 450, 450 150, 500 150 Z", 1000),
        ("ை", "uni0BC8", "M 200 0 C 100 0, 100 200, 200 300 C 300 400, 100 400, 100 600 C 100 800, 300 800, 300 600 C 300 400, 100 400, 200 300 C 300 200, 300 0, 200 0 Z M 200 100 C 250 100, 250 200, 200 250 C 150 200, 150 100, 200 100 Z M 200 500 C 150 500, 150 700, 200 700 C 250 700, 250 500, 200 500 Z", 1000),
        ("ௌ", "uni0BD7", extracted_paths.get('ள', ''), 1000)
    ]
    
    for uni, name, path, width in synthesized_marks:
        if path:
            svg_font_content += f'    <glyph unicode="{uni}" glyph-name="{name}" d="{path.strip()}" horiz-adv-x="{width}" />\n'

    # CRITICAL: Add a SPACE glyph and Punctuation so Word doesn't fallback!
    svg_font_content += '    <glyph unicode=" " glyph-name="space" d="" horiz-adv-x="500" />\n'
    
    punctuation = ".,!?;:'\"-()[]"
    for punct, (tamil_char, _) in zip(punctuation, cycle(positions.items())):
        glyph_path = extracted_paths.get(tamil_char, "")
        if glyph_path:
            svg_font_content += f'    <glyph unicode="{punct}" glyph-name="punct_{ord(punct)}" d="{glyph_path}" horiz-adv-x="1000" />\n'

    # LATIN FALLBACK: Map English characters (a-z, A-Z) to the 31 base handwritten symbols
    # This ensures "The quick brown fox" in Windows Font Viewer shows your handwriting!
    latin_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for latin_char, (tamil_char, _) in zip(latin_chars, cycle(positions.items())):
        char_hex = hex(ord(latin_char))[2:].upper()
        glyph_path = extracted_paths.get(tamil_char, "")
        if glyph_path:
            svg_font_content += f'    <glyph unicode="{latin_char}" glyph-name="lat{char_hex}" d="{glyph_path}" horiz-adv-x="1000" />\n'

    svg_font_content += """  </font>
</defs>
</svg>"""

    with open("output_font/font.svg", "w", encoding="utf-8") as f:
        f.write(svg_font_content)
        
    return True

def build_font():
    try:
        from industrial_font_builder import generate_ttf_python
        success = generate_ttf_python("output_font/font.svg", "output_font/TamilHandwritten.ttf", "TamilHand-Final")
        return success
    except Exception as e:
        print(f"Industrial Build Error: {e}")
        import traceback; traceback.print_exc()
        return False

legacy_30_chars = [
    'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஃ',
    'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம',
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன'
]

# --- API Endpoints ---
@app.get("/api/template")
async def get_template():
    create_template_image("template.png", tamil_chars)
    return FileResponse("template.png", media_type="image/png", filename="tamil-font-template.png")

@app.post("/api/generate-font")
async def generate_font(request: Request, template: UploadFile = File(...)):
    with open("temp_upload.png", "wb") as f:
        f.write(await template.read())
        
    img_check = Image.open("temp_upload.png")
    # New full template (247 chars) is much taller; legacy was < 2000px
    if img_check.height < 2000:
        actual_chars = legacy_30_chars
    else:
        actual_chars = tamil_chars
        
    positions = create_template_image("template_hidden.png", actual_chars)
    success = extract_and_vectorize("temp_upload.png", positions)
    
    if not success:
        return JSONResponse(status_code=400, content={"error": "Invalid template image uploaded."})
        
    font_success = build_font()
    if not font_success:
        return JSONResponse(status_code=500, content={"error": "Error compiling font."})
    
    # Validate the generated font file immediately
    try:
        import importlib
        from fontTools.ttLib import TTFont as _TTFont
        _t = _TTFont("output_font/TamilHandwritten.ttf")
        _glyphs = len(_t.getGlyphOrder())
        _has_dsig = 'DSIG' in _t
        _t.close()
        print(f"Post-build validation: {_glyphs} glyphs, DSIG={_has_dsig}")
        if not _has_dsig or _glyphs < 5:
            print("WARNING: Generated font failed validation! Using last good file as fallback.")
    except Exception as _e:
        print(f"Post-build validation ERROR: {_e} - font is corrupt!")
        return JSONResponse(status_code=500, content={"error": f"Generated font is not valid: {str(_e)}"})
        
    # CRITICAL: Copy to frontend public folder so Next.js can serve it!
    try:
        shutil.copy("output_font/TamilHandwritten.ttf", "frontend/public/TamilHandWritten.ttf")
    except Exception as e:
        print(f"Warning: Failed to copy font to public: {e}")
        
    base_url = str(request.base_url).rstrip("/")
    return {"fontUrl": f"{base_url}/api/fonts/TamilHandwritten.ttf", "fontName": "TamilHand-Final"}

@app.get("/api/fonts/{filename}")
async def get_font(filename: str):
    font_path = os.path.join("output_font", filename)
    if os.path.exists(font_path):
        return FileResponse(
            font_path, 
            media_type="font/ttf", 
            headers={"Access-Control-Allow-Origin": "*"}
        )
    return JSONResponse(status_code=404, content={"error": "Font not found"})

class SaveFontRequest(BaseModel):
    authorName: str
    fontName: str
    fontUrl: str

@app.post("/api/save-font")
async def save_font(request: SaveFontRequest):
    if get_db_connection is None:
        return JSONResponse(status_code=500, content={"error": "Database error"})
        
    try:
        db = get_db_connection()
        fonts_collection = db['fonts']
        
        # Read the generated font off disk
        font_path = "output_font/TamilHandwritten.ttf"
        if not os.path.exists(font_path):
            return JSONResponse(status_code=404, content={"error": "Font file not found on disk"})
            
        with open(font_path, "rb") as f:
            font_bytes = f.read()
            
        new_font = {
            "author_name": request.authorName,
            "font_name": request.fontName,
            "ttf_file": Binary(font_bytes),
            "created_at": datetime.datetime.utcnow()
        }
        fonts_collection.insert_one(new_font)
        return {"success": True, "message": "Font successfully saved to MongoDB"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
