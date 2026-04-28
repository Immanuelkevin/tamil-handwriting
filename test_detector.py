import cv2
import numpy as np

def detect_boxes(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # We want to detect the grey boxes. The grey boxes are dark enough to fall below 220.
    # We will threshold white background, invert to black background, so ink and boxes are white.
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        rect_area = w * h
        if rect_area > 2000 and rect_area < 50000:
            extent = cv2.contourArea(cnt) / rect_area
            # Geometric boxes have high extent. Let's say > 0.85
            if extent > 0.85 and w > 40 and h > 40:
                # To prevent nested boxes, we just take the big ones
                boxes.append((x, y, w, h))
                
    # We might have duplicates or slightly offset ones, let's filter them
    final_boxes = []
    for b in boxes:
        is_dup = False
        for f in final_boxes:
            # If centers are close, it's a duplicate
            if abs(b[0] - f[0]) < 20 and abs(b[1] - f[1]) < 20:
                is_dup = True
                break
        if not is_dup:
            final_boxes.append(b)
            
    # Sort boxes top-to-bottom (y), then left-to-right (x)
    # We define rows by y-coordinate clusters
    if not final_boxes:
        return []
        
    final_boxes.sort(key=lambda b: b[1])
    rows = []
    current_row = [final_boxes[0]]
    for b in final_boxes[1:]:
        if abs(b[1] - current_row[0][1]) < 30: # Same row
            current_row.append(b)
        else:
            rows.append(current_row)
            current_row = [b]
    if current_row:
        rows.append(current_row)
        
    # Sort left-to-right within rows
    sorted_boxes = []
    for row in rows:
        row.sort(key=lambda b: b[0])
        sorted_boxes.extend(row)
        
    return sorted_boxes

boxes = detect_boxes("temp_upload.png")
print("Detected boxes count:", len(boxes))
print("First 10 boxes:", boxes[:10])

