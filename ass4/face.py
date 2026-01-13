import cv2

# Load the pre-trained face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Read image
img = cv2.imread('OIP.webp')

# Check if image loaded
if img is None:
    print("ERROR: Image not found! Check the file path.")
else:
    print(f"✅ Image loaded successfully! Size: {img.shape}")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect faces
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

# Print detection results
print(f"Number of faces detected: {len(faces)}")
print(f"Face coordinates: {faces}")

# Draw rectangles around faces
if len(faces) == 0:
    print("⚠️ No faces detected!")
else:
    print(f"✅ Drawing {len(faces)} rectangle(s)")
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

# Show result
cv2.imshow('Face Detection', img)
cv2.waitKey(0)
cv2.destroyAllWindows()