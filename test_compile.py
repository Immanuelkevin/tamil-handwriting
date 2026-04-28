from server import extract_and_vectorize, legacy_30_chars, create_template_image
import subprocess

p = create_template_image('t.png', legacy_30_chars)
extract_and_vectorize('temp_upload.png', p)

result = subprocess.run('npx svg2ttf output_font/font.svg output_font/TamilHandwritten.ttf', shell=True, capture_output=True, text=True)
print("RC:", result.returncode)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

with open('output_font/font.svg', 'r', encoding='utf-8') as f:
    print("SVG Length:", len(f.read()))

