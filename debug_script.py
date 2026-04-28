import vtracer
import traceback
import sys

try:
    vtracer.convert_image_to_svg_py('template.png', 'test.svg', colormode='binary')
    print("Success")
except Exception as e:
    print("Failed")
    traceback.print_exc()
