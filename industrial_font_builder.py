"""
Industrial-grade TTF font builder using fontTools.
Builds a valid Windows TTF font from an SVG font file.
"""
import os
import re
import shutil
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


def draw_glyph(d_path: str, pen: TTGlyphPen, upm: int) -> bool:
    """Draw SVG path data into a TTGlyphPen. Returns True if any contour was drawn."""
    tokens = re.findall(r'([MLZ])|(-?\d+)', d_path)

    mode = None
    buf = []
    contour_started = False
    any_contour = False

    for cmd, val in tokens:
        if cmd:
            mode = cmd
            if mode == 'Z' and contour_started:
                pen.closePath()
                contour_started = False
                any_contour = True
        elif val and mode in ('M', 'L'):
            buf.append(int(val))
            if len(buf) == 2:
                x, y = buf[0], buf[1]
                buf = []
                if mode == 'M':
                    if contour_started:
                        pen.closePath()
                        any_contour = True
                    pen.moveTo((x, y))
                    contour_started = True
                    mode = 'L'
                elif mode == 'L':
                    pen.lineTo((x, y))

    if contour_started:
        pen.closePath()
        any_contour = True

    return any_contour


def generate_ttf_python(svg_file: str, output_ttf: str, font_name: str = "HandwrittenTamil") -> bool:
    with open(svg_file, 'r', encoding='utf-8') as f:
        svg_text = f.read()

    # Updated regex to include horiz-adv-x attribute
    glyphs_data = re.findall(r'<glyph unicode="(.*?)" glyph-name="(.*?)" d="(.*?)" horiz-adv-x="(.*?)"', svg_text)

    if not glyphs_data:
        # Fallback for old SVGs that might not have the attribute yet
        glyphs_data = re.findall(r'<glyph unicode="(.*?)" glyph-name="(.*?)" d="(.*?)"', svg_text)
        # Add default width of 1000 if missing
        glyphs_data = [(g[0], g[1], g[2], "1000") for g in glyphs_data]

    print(f"Found {len(glyphs_data)} glyphs in SVG")
    ps_name = re.sub(r'[^A-Za-z0-9]', '', font_name)
    UPM = 1000

    fb = FontBuilder(unitsPerEm=UPM)

    glyph_names = [".notdef"] + [g[1] for g in glyphs_data]
    fb.setupGlyphOrder(glyph_names)

    # Character map: Tamil codepoint -> glyph name (filter multi-char strings to avoid ord() crash)
    cmap = {}
    for g in glyphs_data:
        if len(g[0]) == 1:
            cmap[ord(g[0])] = g[1]
        elif len(g[0]) > 1:
            # Ligature handling: map the first char if it doesn't exist, 
            # ideally we should use GSUB but for now we prioritize base chars
            pass
    
    # HACK: Map a-z, A-Z, 0-9 and punctuation to existing Tamil glyphs.
    available_glyphs = [g[1] for g in glyphs_data if g[1] != ".notdef"]
    if available_glyphs:
        latin_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,:;'\"(!?)+-*/="
        for i, char in enumerate(latin_chars):
            if ord(char) not in cmap:
                cmap[ord(char)] = available_glyphs[i % len(available_glyphs)]

    glyphs = {}
    metrics = {".notdef": (500, 0)}

    # .notdef: 500x700 box
    notdef_pen = TTGlyphPen(None)
    notdef_pen.moveTo((50, 0))
    notdef_pen.lineTo((450, 0))
    notdef_pen.lineTo((450, 700))
    notdef_pen.lineTo((50, 700))
    notdef_pen.closePath()
    glyphs[".notdef"] = notdef_pen.glyph()

    empty_count = 0
    for char, name, d_path, adv_width in glyphs_data:
        pen = TTGlyphPen(None)
        has_contours = False

        if d_path.strip():
            try:
                has_contours = draw_glyph(d_path, pen, UPM)
            except Exception as e:
                print(f"  Error drawing {name}: {e}")
                has_contours = False

        if has_contours:
            try:
                glyphs[name] = pen.glyph()
            except Exception as e:
                print(f"  Could not create glyph {name}: {e}")
                glyphs[name] = TTGlyphPen(None).glyph()
                empty_count += 1
        else:
            # Empty glyph - valid, just no visible content
            glyphs[name] = TTGlyphPen(None).glyph()
            empty_count += 1
        
        # Respect the horizontal advance width from the SVG!
        metrics[name] = (int(adv_width), 0)

    print(f"  {len(glyphs) - empty_count - 1} glyphs with content, {empty_count} empty glyphs")

    fb.setupHorizontalMetrics(metrics)
    fb.setupGlyf(glyphs)
    fb.setupCharacterMap(cmap)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({
        "familyName": font_name,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{ps_name}:Version 1.0",
        "fullName": font_name,
        "psName": ps_name,
        "version": "Version 1.0",
    })
    fb.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        sTypoLineGap=0,
        usWinAscent=1000,
        usWinDescent=200,
        sxHeight=500,
        sCapHeight=700,
        usWeightClass=400,
        usWidthClass=5,
        fsType=0,
        # ── Unicode Range bits ──────────────────────────────────────────────
        # ulUnicodeRange1 covers bits 0–31:
        #   bit 0  = Basic Latin (U+0000–U+007F)
        #   bit 7  = Latin Extended Additional
        # ulUnicodeRange3 covers bits 64–95:
        #   bit 73 (= bit 9 of Range3) = Tamil (U+0B80–U+0BFF)  ← KEY FIX
        # Without bit 73 Word's complex-script engine skips this font for Tamil.
        ulUnicodeRange1=0x00000081,  # Basic Latin + Latin Extended Additional
        ulUnicodeRange2=0x00000000,
        ulUnicodeRange3=0x00000200,  # bit 9 of Range3 = Tamil script
        ulUnicodeRange4=0x00000000,
        # ── Code Page Range bits ────────────────────────────────────────────
        # bit 0 = Latin 1252, bit 1 = Latin 2 (for Word compat)
        # bit 17 = Unicode BMP — required so Word accepts the font on any locale
        ulCodePageRange1=0x00020003,  # Latin 1252 + Latin 2 + Unicode BMP
        ulCodePageRange2=0x00000000,
        # fsSelection bit 6 = REGULAR (tells Word this is not Bold/Italic)
        fsSelection=0x0040,
        achVendID=b'DEEP',
        panose={
            'bFamilyType': 3,      # 3 = Script (handwriting)
            'bSerifStyle': 2,
            'bWeight': 4,
            'bProportion': 4,
            'bContrast': 3,
            'bStrokeVariation': 2,
            'bArmStyle': 2,
            'bLetterForm': 2,
            'bMidline': 2,
            'bXHeight': 2,
        },
    )
    fb.setupPost(isFixedPitch=False)
    fb.setupDummyDSIG()

    fb.font['head'].macStyle = 0
    fb.font['head'].flags = 0x000B

    fb.save(output_ttf)

    # Validate that the saved file is readable
    try:
        from fontTools.ttLib import TTFont
        t = TTFont(output_ttf)
        n_glyphs = len(t.getGlyphOrder())
        has_dsig = 'DSIG' in t
        print(f"Validation: {n_glyphs} glyphs, DSIG={has_dsig} -> {'OK' if has_dsig else 'WARN: no DSIG'}")
        t.close()
    except Exception as e:
        print(f"Validation FAILED: {e}")
        return False

    print(f"SUCCESS: {output_ttf}")
    return True


if __name__ == "__main__":
    ok = generate_ttf_python("output_font/font.svg", "output_font/TamilPython.ttf", "Handwriting-FinalFix")
    if ok:
        shutil.copy("output_font/TamilPython.ttf", "output_font/TamilHandwritten.ttf")
        shutil.copy("output_font/TamilPython.ttf", "frontend/public/TamilHandWritten.ttf")
        print("All copies done.")
