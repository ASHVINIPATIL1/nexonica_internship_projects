import cv2

img = cv2.imread('image.png')
cv2.imshow("image",  img)
h, w, c = img.shape
print(w, h, c)
for y in range(h):
    for x in range(w):
        b, g, r = img[y][x]
        avg = (int(b) + int(g) + int(r)) /3

        img[y][x] = (avg, avg, avg)  # gray
        # img[y][x] = (b, avg, avg)  blueish
        # img[y][x] = (avg, g, avg)  greenish
        # img[y][x] = (avg, avg, r)  redish
        # img[y][w - x - 1] = (b, g, r)   mirror
cv2.imshow("image_gray", img)
cv2.waitKey(0)
cv2.destriyAllWindows()