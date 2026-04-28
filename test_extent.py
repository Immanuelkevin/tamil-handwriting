import cv2
import numpy as np

# Create a mock 100x100 crop with a hollow square border and a blue circle inside
img = np.ones((100, 100, 3), dtype=np.uint8) * 255
# Draw dark grey box (the grid)
cv2.rectangle(img, (10, 10), (90, 90), (100, 100, 100), 2)
# Draw bright blue handwriting (a huge circle O)
cv2.circle(img, (50, 50), 35, (255, 0, 0), 6)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Bright blue is ~76 in BGR2GRAY. Wait. BGR: (255, 0, 0) is Blue.
# OpenCV converts BGR to GRAY using 0.114*B + 0.587*G + 0.299*R = 0.114*255 = 29!!
# Wait! Pure blue is INCREDIBLY DARK in grayscale (intensity 29)!
# Let's check a standard light blue: (255, 128, 0) -> 0.114*255 + 0.587*128 + 0.299*0 = 29+75 = 104.
# If they used bright blue '#00a8ff' -> RGB(0, 168, 255) -> BGR(255, 168, 0).
# Grayscale = 0.114*255 + 0.587*168 = 29 + 98 = 127.

_, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)

contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    if len(cnt) > 2:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        rect_area = w * h
        if rect_area > 0:
            extent = area / rect_area
            print(f"Contour - w:{w} h:{h} Area:{area} RectArea:{rect_area} Extent:{extent:.2f}")

