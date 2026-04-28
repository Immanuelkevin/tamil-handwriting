import streamlit as st
import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
import vtracer
import datetime
from bson.binary import Binary
try:
    from db import get_db_connection
except ImportError:
    get_db_connection = None

# Set up Tamil Characters and their Unicode points
# Full Tamil script: 12 Vowels + 1 Aytham + 18 Consonants + 216 Uyirmei (18x12) = 247 characters
tamil_chars = [
    # ── SECTION 1: Pure Vowels / Uyir (12) ──
    'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',

    # ── SECTION 2: Aytham (1) ──
    'ஃ',

    # ── SECTION 3: Pure Consonants / Mei (18) ──
    'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம',
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன',

    # ── SECTION 4: Uyirmei (Consonant + Vowel combinations, 18 × 12 = 216) ──
    # Each consonant row: [a, aa, i, ii, u, uu, e, ee, ai, o, oo, au]

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

# Windows standard Tamil font for the template
FONT_PATH = "nirmala.ttf"
if not os.path.exists("C:\\Windows\\Fonts\\nirmala.ttf"):
    # Fallback if nirmala.ttf isn't directly found, use arial (though arial doesn't render tamil well)
    FONT_PATH = "arial.ttf"
else:
    FONT_PATH = "C:\\Windows\\Fonts\\nirmala.ttf"

def create_template_image(output_path):
    font_size = 40
    image_width = 1000
    rows = (len(tamil_chars) + 5) // 6
    image_height = rows * 200 + 100
    template_image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(template_image)
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except IOError:
        font = ImageFont.load_default()

    x_start = 50
    y_start = 50
    box_size = 100
    spacing = 50
    
    x, y = x_start, y_start
    positions = {}

    for char in tamil_chars:
        # Draw text description/character above box
        draw.text((x + 30, y - font_size - 10), char, fill="black", font=font)
        # Draw box
        box_coords = (x, y, x + box_size, y + box_size)
        draw.rectangle(box_coords, outline="black")
        positions[char] = box_coords
        
        x += box_size + spacing
        if x > image_width - box_size - spacing:
            x = x_start
            y += box_size + spacing + 50

    template_image.save(output_path)
    return positions

def extract_and_vectorize(filled_image_path, positions):
    img = Image.open(filled_image_path)
    
    # Calculate expected template size
    image_width = 1000
    rows = (len(tamil_chars) + 5) // 6
    image_height = rows * 200 + 100
    
    # Check if user uploaded the old template (old one had only 67 boxes)
    # New template with 247 chars will be much taller
    if img.height < 5000 and len(tamil_chars) > 200:
        st.error("⚠️ It looks like you uploaded the OLD template! Please download the NEW template (which is taller and has 247 boxes for the full Tamil script) and upload that instead.")
        return False
        
    # Strictly resize width to 1000 to maintain X coordinates, scale Y proportionally if needed
    if img.width != image_width:
        aspect_ratio = img.height / img.width
        img = img.resize((image_width, int(image_width * aspect_ratio)))
        
    os.makedirs("extracted_images", exist_ok=True)
    os.makedirs("output_font", exist_ok=True)
    
    import cv2
    import numpy as np
    
    extracted_paths = {}
    
    # We will build an SVG Font file directly
    svg_font_content = f"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >
<svg xmlns="http://www.w3.org/2000/svg">
<defs>
  <font id="TamilHand-Final" horiz-adv-x="1000">
    <font-face font-family="TamilHand-Final" units-per-em="1000" ascent="800" descent="-200" />
    <missing-glyph horiz-adv-x="1000" />
"""
    
    for char, pos in positions.items():
        # Crop slightly inside the box (5px padding) to completely avoid the printed black border
        pad = 5
        clean_pos = (pos[0] + pad, pos[1] + pad, pos[2] - pad, pos[3] - pad)
        crop = img.crop(clean_pos)
        
        # Handle multi-codepoint characters (e.g., consonants with modifiers like கு)
        char_hex = "_".join([hex(ord(c))[2:].upper() for c in char])
        char_name = f"uni{char_hex}"
        png_path = f"extracted_images/{char_name}.png"
        crop.save(png_path)
        
        cv_img = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)
        # Use 140 instead of 150 to make the lines look thinner and more natural
        _, thresh = cv2.threshold(cv_img, 140, 255, cv2.THRESH_BINARY_INV)
        
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        h, w = cv_img.shape
        scale_x = 1000.0 / w
        scale_y = 1000.0 / h
        
        d_all = ""
        for cnt in contours:
            if len(cnt) > 2:
                pts = cnt.reshape(-1, 2)
                # Map coordinates: Y goes UP in SVG fonts!
                start_x = int(pts[0][0] * scale_x)
                start_y = int(800 - (pts[0][1] * scale_y))
                d_all += f"M{start_x} {start_y} "
                
                for pt in pts[1:]:
                    pt_x = int(pt[0] * scale_x)
                    pt_y = int(800 - (pt[1] * scale_y))
                    d_all += f"L{pt_x} {pt_y} "
                d_all += "Z "
                
        # Inject glyph into SVG Font
        svg_font_content += f'    <glyph unicode="{char}" glyph-name="{char_name}" d="{d_all.strip()}" horiz-adv-x="1000" />\n'
        extracted_paths[char] = d_all.strip()
        
    # AUTOMATIC SYNTHESIS OF ALL 216 VARIATIONS
    # We mathematically build the 10 Vowel Modifiers so the OS automatically creates combinations!
    synthesized_marks = [
        # Pulli (Dot for consonants like க்)
        ("்", "uni0BCD", "M 450 700 C 400 700, 400 800, 450 800 C 500 800, 500 700, 450 700 Z"),
        # Aa (Thunaikkal ா) -> Borrow the letter 'ர'
        ("ா", "uni0BBE", extracted_paths.get('ர', '')),
        # I (Top Arc ி)
        ("ி", "uni0BBF", "M 800 600 C 800 1000, 300 1000, 300 600 L 400 600 C 400 850, 700 850, 700 600 Z"),
        # Ii (Top Arc + loop ீ)
        ("ீ", "uni0BC0", "M 800 600 C 800 1000, 300 1000, 300 600 L 400 600 C 400 850, 700 850, 700 600 Z M 600 850 C 500 850, 500 1000, 600 1000 C 700 1000, 700 850, 600 850 Z"),
        # U (Bottom hook ு) - Fallback
        ("ு", "uni0BC1", "M 700 0 C 700 -400, 200 -400, 200 -100 L 300 -100 C 300 -300, 600 -300, 600 0 Z"),
        # Uu (Bottom hook + loop ூ) - Fallback
        ("ூ", "uni0BC2", "M 700 0 C 700 -400, 200 -400, 200 -100 L 300 -100 C 300 -300, 600 -300, 600 0 Z M 600 -100 C 500 -100, 500 -300, 600 -300 C 700 -300, 700 -100, 600 -100 Z"),
        # E (Ottrai Kombu ெ)
        ("ெ", "uni0BC6", "M 300 100 C 200 100, 200 400, 300 400 C 400 400, 400 700, 300 700 C 200 700, 200 500, 300 500 L 300 600 C 250 600, 250 650, 300 650 C 350 650, 350 450, 300 450 C 250 450, 250 150, 300 150 Z"),
        # Ee (Rettai Kombu ே) -> Shifted double Ottrai Kombu
        ("ே", "uni0BC7", "M 300 100 C 200 100, 200 400, 300 400 C 400 400, 400 700, 300 700 C 200 700, 200 500, 300 500 L 300 600 C 250 600, 250 650, 300 650 C 350 650, 350 450, 300 450 C 250 450, 250 150, 300 150 Z M 500 100 C 400 100, 400 400, 500 400 C 600 400, 600 700, 500 700 C 400 700, 400 500, 500 500 L 500 600 C 450 600, 450 650, 500 650 C 550 650, 550 450, 500 450 C 450 450, 450 150, 500 150 Z"),
        # Ai (Changili Kombu ை)
        ("ை", "uni0BC8", "M 200 0 C 100 0, 100 200, 200 300 C 300 400, 100 400, 100 600 C 100 800, 300 800, 300 600 C 300 400, 100 400, 200 300 C 300 200, 300 0, 200 0 Z M 200 100 C 250 100, 250 200, 200 250 C 150 200, 150 100, 200 100 Z M 200 500 C 150 500, 150 700, 200 700 C 250 700, 250 500, 200 500 Z"),
        # Au length (ௌ modifier is the same as Lla ள)
        ("ௌ", "uni0BD7", extracted_paths.get('ள', ''))
    ]
    
    for uni, name, path in synthesized_marks:
        if path:
            svg_font_content += f'    <glyph unicode="{uni}" glyph-name="{name}" d="{path.strip()}" horiz-adv-x="1000" />\n'
            
    # Re-added Latin characters mapped to your handwriting so English typing (dfdf) works!
    latin_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    from itertools import cycle
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

def build_font(codepoints_ignored):
    # Convert directly via svg2ttf
    try:
        subprocess.run('cmd /c "npx svg2ttf output_font/font.svg output_font/TamilHandwritten.ttf"', shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

st.set_page_config(page_title="Tamil Font Generator", layout="wide")
st.title("🖌️ Handwritten Tamil Font Generator")
st.markdown("Create fully scalable digital Tamil fonts from your handwriting using modern image processing and vectorization.")

tab1, tab2 = st.tabs(["1. Get Template", "2. Upload & Generate Font"])

with tab1:
    st.header("Step 1: Download Handwriting Template")
    st.write("First, download the template below. Print it out or open it in a digital drawing app, and write the corresponding Tamil character inside each box.")
    if st.button("Generate Template"):
        positions = create_template_image("template.png")
        st.image("template.png", caption="Tamil Handwriting Template", width=700)
        with open("template.png", "rb") as f:
            st.download_button("⬇️ Download Template.png", f, "template.png", "image/png")

with tab2:
    st.header("Step 2: Upload Filled Template")
    uploaded_file = st.file_uploader("Upload your completed template (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Template", width=700)
        
        if st.button("✨ Generate Font ✨"):
            with st.spinner("Extracting handwritten characters..."):
                with open("temp_upload.png", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Regenerate positions
                positions = create_template_image("template_hidden.png")
                
                # Process
                codepoints = extract_and_vectorize("temp_upload.png", positions)
                
            if codepoints is False:
                st.stop()
            
            with st.spinner("Vectorizing characters and building TrueType Font..."):
                success = build_font(codepoints)
                
            if success and os.path.exists("output_font/TamilHandwritten.ttf"):
                st.success("Font generated successfully!")
                
                # Show live preview using the generated font
                import base64
                with open("output_font/TamilHandwritten.ttf", "rb") as f:
                    font_bytes = f.read()
                b64_font = base64.b64encode(font_bytes).decode()
                
                import time
                busted_font_name = f'TamilHand-Final-{int(time.time())}'
                
                custom_css = f"""
                <style>
                @font-face {{
                    font-family: '{busted_font_name}';
                    src: url(data:font/ttf;charset=utf-8;base64,{b64_font}) format('truetype');
                }}
                .tamil-preview-box {{
                    font-size: 50px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border: 2px dashed #4CAF50;
                    border-radius: 10px;
                    background-color: #f0fdf4;
                    color: black;
                    line-height: 1.5;
                    max-height: 400px;
                    overflow-y: auto;
                    overflow-x: hidden;
                }}
                .tamil-text {{
                    font-family: '{busted_font_name}';
                }}
                .english-label {{
                    font-family: sans-serif;
                    font-size: 20px;
                    font-weight: bold;
                    display: block;
                    margin-top: 15px;
                }}
                </style>
                <h3>Live Preview:</h3>
                <div class="tamil-preview-box">
                    <span class="english-label">1. Pure Vowels / Uyir (12) + Aytham (1):</span>
                    <span class="tamil-text">அ ஆ இ ஈ உ ஊ எ ஏ ஐ ஒ ஓ ஔ ஃ</span><br>
                    <span class="english-label">2. Pure Consonants / Mei (18):</span>
                    <span class="tamil-text">க ங ச ஞ ட ண த ந ப ம ய ர ல வ ழ ள ற ன</span><br>
                    <span class="english-label">3. Full Uyirmei Matrix (18 consonants × 12 vowels = 216):</span>
                    <span class="tamil-text">க கா கி கீ கு கூ கெ கே கை கொ கோ கௌ</span><br>
                    <span class="tamil-text">ங ஙா ஙி ஙீ ஙு ஙூ ஙெ ஙே ஙை ஙொ ஙோ ஙௌ</span><br>
                    <span class="tamil-text">ச சா சி சீ சு சூ செ சே சை சொ சோ சௌ</span><br>
                    <span class="tamil-text">ஞ ஞா ஞி ஞீ ஞு ஞூ ஞெ ஞே ஞை ஞொ ஞோ ஞௌ</span><br>
                    <span class="tamil-text">ட டா டி டீ டு டூ டெ டே டை டொ டோ டௌ</span><br>
                    <span class="tamil-text">ண ணா ணி ணீ ணு ணூ ணெ ணே ணை ணொ ணோ ணௌ</span><br>
                    <span class="tamil-text">த தா தி தீ து தூ தெ தே தை தொ தோ தௌ</span><br>
                    <span class="tamil-text">ந நா நி நீ நு நூ நெ நே நை நொ நோ நௌ</span><br>
                    <span class="tamil-text">ப பா பி பீ பு பூ பெ பே பை பொ போ பௌ</span><br>
                    <span class="tamil-text">ம மா மி மீ மு மூ மெ மே மை மொ மோ மௌ</span><br>
                    <span class="tamil-text">ய யா யி யீ யு யூ யெ யே யை யொ யோ யௌ</span><br>
                    <span class="tamil-text">ர ரா ரி ரீ ரு ரூ ரெ ரே ரை ரொ ரோ ரௌ</span><br>
                    <span class="tamil-text">ல லா லி லீ லு லூ லெ லே லை லொ லோ லௌ</span><br>
                    <span class="tamil-text">வ வா வி வீ வு வூ வெ வே வை வொ வோ வௌ</span><br>
                    <span class="tamil-text">ழ ழா ழி ழீ ழு ழூ ழெ ழே ழை ழொ ழோ ழௌ</span><br>
                    <span class="tamil-text">ள ளா ளி ளீ ளு ளூ ளெ ளே ளை ளொ ளோ ளௌ</span><br>
                    <span class="tamil-text">ற றா றி றீ று றூ றெ றே றை றொ றோ றௌ</span><br>
                    <span class="tamil-text">ன னா னி னீ னு னூ னெ னே னை னொ னோ னௌ</span><br>
                </div>
                """
                st.components.v1.html(custom_css, height=800)

                with open("output_font/TamilHandwritten.ttf", "rb") as f:
                    st.download_button(
                        label="📥 Download TamilHandwritten.ttf",
                        data=f,
                        file_name="TamilHandwritten.ttf",
                        mime="font/ttf"
                    )
                
                st.markdown("---")
                st.subheader("☁️ Save to Cloud")
                st.write("Archive your custom font to MongoDB so you never lose it.")
                author_name = st.text_input("Author Name", placeholder="e.g., Praba")
                font_name_input = st.text_input("Font Name", placeholder="e.g., My Awesome Tamil Font")
                
                if st.button("💾 Save to MongoDB"):
                    if not author_name or not font_name_input:
                        st.warning("Please provide both an author name and a font name before saving!")
                    elif get_db_connection is None:
                        st.error("Database connection module is missing.")
                    else:
                        with st.spinner("Uploading to MongoDB..."):
                            try:
                                db = get_db_connection()
                                if db is None:
                                    st.error("Could not connect to MongoDB database. Check credentials.")
                                else:
                                    fonts_collection = db['fonts']
                                    new_font = {
                                        "author_name": author_name,
                                        "font_name": font_name_input,
                                        "ttf_file": Binary(font_bytes),
                                        "created_at": datetime.datetime.utcnow()
                                    }
                                    fonts_collection.insert_one(new_font)
                                    st.success(f"Font '{font_name_input}' successfully saved to MongoDB!")
                            except Exception as e:
                                st.error(f"MongoDB Error: {e}")
            else:
                st.error("There was an error generating the font. Please check the terminal logs.")
