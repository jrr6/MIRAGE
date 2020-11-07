import numpy as np
import cv2
from matplotlib import pyplot as plt

im = cv2.imread('test.jpg')

new_width = 400
height = int(new_width / im.shape[1] * im.shape[0])
dim = (new_width, height)
im = cv2.resize(im, dim, interpolation=cv2.INTER_AREA)

imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# ret, thresh = cv2.threshold(imgray, 50, 255, 0)
thresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 7)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
filteredContours = []
# https://answers.opencv.org/question/65005/in-python-how-can-i-reduce-a-list-of-contours-to-those-of-a-specified-size/
for cnt in contours:
    heightMin = 50
    widthMin = 50
    rect = cv2.minAreaRect(cnt)
    width = rect[1][0]
    height = rect[1][1]
    if (width >= widthMin) and (height > heightMin):
        filteredContours.append(cnt)
im = np.zeros_like(im)
cv2.drawContours(im, filteredContours, -1, (0,255,0), 3)

# https://docs.opencv.org/4.5.0/d4/d73/tutorial_py_contours_begin.html
kernel = np.ones((5,5),np.float32)/25
dst = cv2.filter2D(im,-1,kernel)
edges = cv2.Canny(dst,200,300)

for yPixel in range(len(edges)):
    for xPixel in range(len(edges[yPixel])):
        if edges[yPixel][xPixel] > 0:
            print('*', end='')
        else:
            print('-', end='')
    print()

# plt.subplot(121),plt.imshow(im,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges,cmap = 'gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
# plt.show()

cv2.imshow('test', im)
cv2.waitKey(0)
