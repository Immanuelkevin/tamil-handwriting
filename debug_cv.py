import cv2
from PIL import Image
from server import tamil_chars, create_template_image

actual_chars = [
    'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஃ',
    'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம',
    'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன'
]

positions = create_template_image("template_hidden.png", actual_chars)
img = Image.open("temp_upload.png")
image_width = 1000
aspect_ratio = img.height / img.width
img = img.resize((image_width, int(image_width * aspect_ratio)))

print("Expected positions:", positions['க'])

pos = positions['க']
pad = 5
clean_pos = (pos[0] + pad, pos[1] + pad, pos[2] - pad, pos[3] - pad)
crop = img.crop(clean_pos)
crop.save('debug_crop_ka.png')

cv_img = cv2.imread('debug_crop_ka.png', cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(cv_img, 150, 255, cv2.THRESH_BINARY_INV)
thresh[0:4, :] = 0
thresh[-4:, :] = 0
thresh[:, 0:4] = 0
thresh[:, -4:] = 0

contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print(f"Num contours on Ka: {len(contours)}")
for cnt in contours:
    if len(cnt) > 2:
        print(f"Area: {cv2.contourArea(cnt)}")
