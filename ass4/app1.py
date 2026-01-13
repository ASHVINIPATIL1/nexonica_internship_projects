import cv2

img = cv2.imread('image.png', cv2.IMREAD_COLOR)
# img = cv2.imread('image.png')
# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
 
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destriyAllWindows()

