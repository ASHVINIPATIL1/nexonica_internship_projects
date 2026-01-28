import cv2
import numpy as np
import easyocr

# ----------------------------
# 1. Load image
# ----------------------------
img = cv2.imread("input.png")
if img is None:
    raise Exception("Image not found. Check filename/path.")

original = img.copy()

# ----------------------------
# 2. Convert to HSV & extract YELLOW drawing
# ----------------------------
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Yellow color range (tuned for air-drawn yellow)
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([35, 255, 255])

mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

# ----------------------------
# 3. Clean the mask
# ----------------------------
kernel = np.ones((3, 3), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.dilate(mask, kernel, iterations=2)

# ----------------------------
# 4. OCR on extracted drawing
# ----------------------------
reader = easyocr.Reader(['en'])
results = reader.readtext(mask, detail=1)

print("OCR Results:", results)

# ----------------------------
# 5. Remove handwritten text
# ----------------------------
clean_img = original.copy()

# Paint over detected drawing (wall-like gray)
clean_img[mask > 0] = (200, 200, 200)

# ----------------------------
# 6. Overlay digital text
# ----------------------------
for bbox, text, confidence in results:
    if confidence < 0.3:
        continue

    # Bounding box points
    (tl, tr, br, bl) = bbox
    x = int(tl[0])
    y = int(tl[1])
    h = int(bl[1] - tl[1])

    # Scale font based on drawing size
    font_scale = max(1, h / 25)

    cv2.putText(
        clean_img,
        text,
        (x, y + h),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        3,
        cv2.LINE_AA
    )

# ----------------------------
# 7. Save final output
# ----------------------------
cv2.imwrite("output_digital_overlay.png", clean_img)

print("✅ Done! Saved as output_digital_overlay.png")
