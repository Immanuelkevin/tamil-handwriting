import vtracer
input_image = "letters.png"
output_svg = "letters.svg"
vtracer.convert_image_to_svg_py(
    input_image,
    output_svg,
    colormode="binary"
)
print("SVG created successfully")

