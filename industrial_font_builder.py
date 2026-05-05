"""
Industrial-grade TTF font builder using fontTools.
Builds a valid Windows TTF font from an SVG font file.
"""
import os
import re
import shutil
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.ttLib import newTable


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
        glyphs_data = re.findall(r'<glyph unicode="(.*?)" glyph-name="(.*?)" d="(.*?)"', svg_text)
        glyphs_data = [(g[0], g[1], g[2], "1000") for g in glyphs_data]

    print(f"Found {len(glyphs_data)} glyphs in SVG")
    ps_name = re.sub(r'[^A-Za-z0-9]', '', font_name)
    UPM = 1000

    # ── Step 1: build char→glyph map from single-char glyphs ──────────────────
    char_to_glyph = {}
    for g in glyphs_data:
        if len(g[0]) == 1:
            char_to_glyph[g[0]] = g[1]

    # ── Step 2: find combining marks used in multi-char glyphs but missing as
    #   standalone glyphs (e.g. ா U+0BBE, ி U+0BBF, ு U+0BC1, ் U+0BCD …).
    #   Without their own glyph entries the GSUB rules can never reference them.
    missing_chars = set()
    for g in glyphs_data:
        if len(g[0]) >= 2:
            for c in g[0]:
                if c not in char_to_glyph:
                    missing_chars.add(c)

    # Synthesise zero-width placeholder glyphs for all missing combining marks
    placeholder_data = []   # list of (char, glyph_name)
    for c in sorted(missing_chars, key=ord):
        name = f"uni{ord(c):04X}"
        char_to_glyph[c] = name
        placeholder_data.append((c, name))
        print(f"  Synthesising zero-width glyph for U+{ord(c):04X} ({c})")

    # Extend glyphs_data with placeholders so the rest of the pipeline sees them
    extra_data = [(c, name, "", "0") for c, name in placeholder_data]
    all_glyph_data = glyphs_data + extra_data

    fb = FontBuilder(unitsPerEm=UPM)

    glyph_names = [".notdef"] + [g[1] for g in all_glyph_data]
    fb.setupGlyphOrder(glyph_names)

    # Character map: single-char glyphs + zero-width combining mark placeholders
    cmap = {}
    for g in glyphs_data:
        if len(g[0]) == 1:
            cmap[ord(g[0])] = g[1]
    # Also add the synthesised combining mark placeholders
    for c, name in placeholder_data:
        cmap[ord(c)] = name

    # Map space to a blank glyph
    cmap[0x0020] = "space"
    
    # Do NOT map a-z, A-Z, 0-9 to Tamil glyphs. This was causing spaces/Latin chars
    # to render as Tamil characters. Instead, just leave them unmapped so they 
    # use system fallbacks or show nothing, which is better than wrong glyphs.

    # 1. Define glyph order and dictionaries
    # Glyph index 0 MUST be .notdef for Windows compatibility.
    glyphs = {}
    metrics = {}

    # .notdef: 500x700 box
    notdef_pen = TTGlyphPen(None)
    notdef_pen.moveTo((50, 0))
    notdef_pen.lineTo((450, 0))
    notdef_pen.lineTo((450, 700))
    notdef_pen.lineTo((50, 700))
    notdef_pen.closePath()
    glyphs[".notdef"] = notdef_pen.glyph()
    metrics[".notdef"] = (500, 0)

    # space: empty glyph
    space_pen = TTGlyphPen(None)
    glyphs["space"] = space_pen.glyph()
    metrics["space"] = (500, 0)

    empty_count = 0
    for char, name, d_path, adv_width in all_glyph_data:
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
            glyphs[name] = TTGlyphPen(None).glyph()
            empty_count += 1

        # Calculate the actual width of the handwriting (Smart Spacing)
        # We find the min/max X of the contours and add a small side bearing.
        from fontTools.pens.boundsPen import BoundsPen
        bp = BoundsPen(None)
        if d_path:
            draw_glyph(d_path, bp, UPM)
            if bp.bounds:
                x_min, y_min, x_max, y_max = bp.bounds
                # Set width to (right edge - left edge) + some breathing room
                # We also shift the glyph to the left so it starts at X=50
                actual_width = (x_max - x_min) + 100 
                metrics[name] = (int(actual_width), 0)
            else:
                metrics[name] = (500, 0)
        else:
            metrics[name] = (500, 0)

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

    # --- Add OpenType Features (GSUB for Tamil Ligatures) ---
    # char_to_glyph already has ALL chars including synthesised combining marks.
    #
    # Tamil tml2 shaping pipeline (Uniscribe/DirectWrite/HarfBuzz):
    #   ccmp / akhn  → fire on ORIGINAL Unicode order (before reordering)
    #   pres / psts  → fire AFTER Uniscribe reorders pre-base vowels
    #                  For pre-base vowels (ெ ே ை), after reorder the sequence
    #                  is [vowel][consonant], so pres rule must be:
    #                      sub vowel consonant by combined_glyph;   ← REVERSED
    #   psts         → post-base vowels stay after consonant, so:
    #                      sub consonant vowel by combined_glyph;   ← original order

    PRE_BASE_SIGNS  = set("\u0BC6\u0BC7\u0BC8")   # e, ee, ai  — reordered before consonant
    POST_BASE_SIGNS = set("\u0BBE\u0BBF\u0BC0\u0BC1\u0BC2\u0BCA\u0BCB\u0BCC\u0BD7")
    VIRAMA = "\u0BCD"

    subs_akhn = []   # consonant + virama → fires before reorder, original order
    subs_pres = []   # [vowel][consonant] → REVERSED (post-reorder form)
    subs_psts = []   # [consonant][vowel] → original order
    subs_ccmp = []   # all in original order → fires before reorder (fallback)

    for g in glyphs_data:
        if len(g[0]) < 2:
            continue
        seq = []
        for c in g[0]:
            if c in char_to_glyph:
                seq.append(char_to_glyph[c])
            else:
                seq = None
                break
        if not seq:
            continue

        second = g[0][1]
        if second == VIRAMA:
            subs_akhn.append((seq, g[1]))
        elif second in PRE_BASE_SIGNS:
            # pres fires after reordering → vowel comes first
            reversed_seq = [seq[1], seq[0]]  # swap consonant and vowel
            subs_pres.append((reversed_seq, g[1]))
        elif second in POST_BASE_SIGNS:
            subs_psts.append((seq, g[1]))
        subs_ccmp.append((seq, g[1]))  # ccmp fires before reordering → original order

    # --- Build GDEF table to mark combining chars as Mark class (class 3) ---
    # This is essential: without GDEF, Uniscribe doesn't know ா ி etc are marks
    ALL_COMBINING = set("\u0BBE\u0BBF\u0BC0\u0BC1\u0BC2\u0BC6\u0BC7\u0BC8\u0BCA\u0BCB\u0BCC\u0BCD\u0BD7")
    mark_glyph_names = []
    for c in ALL_COMBINING:
        if c in char_to_glyph:
            mark_glyph_names.append(char_to_glyph[c])

    if mark_glyph_names:
        from fontTools.ttLib.tables import otTables
        gdef = otTables.GDEF()
        gdef.Version = 0x00010000
        gdef.GlyphClassDef = otTables.GlyphClassDef()
        gdef.GlyphClassDef.classDefs = {}
        for name in mark_glyph_names:
            gdef.GlyphClassDef.classDefs[name] = 3  # 3 = Mark
        gdef.AttachList = None
        gdef.LigCaretList = None
        gdef.MarkAttachClassDef = None
        gdef_table = newTable("GDEF")
        gdef_table.table = gdef
        fb.font["GDEF"] = gdef_table
        print(f"  GDEF: classified {len(mark_glyph_names)} combining marks as Mark (class 3)")

    def build_feature(tag, subs):
        out = f"feature {tag} {{\n"
        for seq, target in subs:
            out += f"    sub {' '.join(seq)} by {target};\n"
        out += f"}} {tag};\n\n"
        return out

    fea_text = (
        # Register ONLY under DFLT — do NOT add taml/tml2 here.
        # When a font has no taml/tml2 script, Windows Uniscribe falls back to
        # DFLT shaping.  Under DFLT there is no Tamil-specific reordering, so
        # the glyph sequence stays in original Unicode order and our ccmp rules
        # (which are also written in original order) fire and produce the correct
        # combined handwritten glyphs.  If we register taml/tml2, Uniscribe takes
        # over with its own built-in Tamil shaping engine which ignores our rules.
        "languagesystem DFLT dflt;\n\n"
    )
    # Under DFLT: ccmp fires before any reordering (there is none), so original
    # Unicode order [consonant][vowel] matches our rules exactly.
    if subs_ccmp:
        fea_text += build_feature("ccmp", subs_ccmp)
        fea_text += build_feature("liga", subs_ccmp)
    # akhn fires early even in DFLT
    if subs_akhn:
        fea_text += build_feature("akhn", subs_akhn)

    total_subs = len(subs_akhn) + len(subs_pres) + len(subs_psts)
    print(f"  GSUB: {total_subs} targeted subs + {len(subs_ccmp)} ccmp/liga fallbacks")

    try:
        with open("features.fea", "w", encoding="utf-8") as fea_file:
            fea_file.write(fea_text)
        addOpenTypeFeatures(fb.font, "features.fea")
        print("Successfully added GSUB features (akhn, pres[reversed], psts, ccmp, liga).")
    except Exception as e:
        print(f"Error adding OpenType features: {e}")
    # --------------------------------------------------------

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
    ok = generate_ttf_python("output_font/font.svg", "output_font/TamilPython.ttf", "Handwriting-Clean")
    if ok:
        shutil.copy("output_font/TamilPython.ttf", "output_font/TamilHandwritten.ttf")
        shutil.copy("output_font/TamilPython.ttf", "frontend/public/TamilHandWritten.ttf")
        print("All copies done.")
