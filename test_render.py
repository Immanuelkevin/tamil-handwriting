from PIL import Image, ImageDraw, ImageFont
import os

font_path = "output_font/TamilHandwritten.ttf"
output_path = "debug_render.png"

if os.path.exists(font_path):
    try:
        # Create a blank image
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Load the generated font
        font = ImageFont.truetype(font_path, 40)
        
        # Draw some Latin text and some Tamil text
        test_text = "abc அஆஇ"
        draw.text((10, 50), test_text, fill='black', font=font)
        
        img.save(output_path)
        print(f"Success! Rendered test to {output_path}")
    except Exception as e:
        print(f"Error rendering: {e}")
else:
    print(f"Font file not found at {font_path}")
