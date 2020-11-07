import math
import colour

import numpy as np
import cv2
from matplotlib import pyplot as plt
import numpy as np
from colortemp import tempFromRGB
import colorsys

# imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
# # ret, thresh = cv2.threshold(imgray, 50, 255, 0)
# thresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 7)
# contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# filteredContours = []
# # https://answers.opencv.org/question/65005/in-python-how-can-i-reduce-a-list-of-contours-to-those-of-a-specified-size/
# for cnt in contours:
#     heightMin = 50
#     widthMin = 50
#     rect = cv2.minAreaRect(cnt)
#     width = rect[1][0]
#     height = rect[1][1]
#     if (width >= widthMin) and (height > heightMin):
#         filteredContours.append(cnt)
# im = np.zeros_like(im)
# cv2.drawContours(im, filteredContours, -1, (0,255,0), 3)

# https://docs.opencv.org/4.5.0/d4/d73/tutorial_py_contours_begin.html

def fetchTestImage():
    im = cv2.imread('test.jpg')

    new_width = 400
    height = int(new_width / im.shape[1] * im.shape[0])
    dim = (new_width, height)
    im = cv2.resize(im, dim, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((4,4), np.float32) / 16
    blurred = cv2.filter2D(gray, -1, kernel)
    # blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # https://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
    v = np.median(im)
    # apply automatic Canny edge detection using the computed median
    sigma = 0.33
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    # edges = cv2.Canny(blurred, 200, 300)
    # edges = cv2.Canny(blurred, 50, 100)
    edges = cv2.Canny(blurred, lower, upper)

    plt.subplot(121), plt.imshow(blurred, cmap='gray')
    plt.subplot(122), plt.imshow(edges, cmap='gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    plt.show()

    i = 0
    while len(np.nonzero(edges[i])[0]) == 0:
        edges = np.delete(edges, i, 0)

    i = -1
    while len(np.nonzero(edges[i])[0]) == 0:
        edges = np.delete(edges, i, 0)

    result = [[]]
    for yPixel in range(len(edges)):
        for xPixel in range(len(edges[yPixel])):
            if edges[yPixel][xPixel] > 0:
                result[-1].append(True)
            else:
                result[-1].append(False)
        result.append([])
        # print()
    result.pop()

    h = im.shape[0]
    w = im.shape[1]

    chordPartitionSize = w // 4

    totalWarmth = 0
    totalHLS = np.array([0.0, 0.0, 0.0])
    hlsPartitions = np.zeros((4, 4))  # h, l, s, count
    totalCount = 0

    # loop over the image, pixel by pixel
    for x in range(0, w):
        for y in range(0, h):
            b, g, r = im[y, x]
            totalWarmth += min(tempFromRGB(r, g, b), 10000)
            hls = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            totalHLS += hls
            totalCount += 1

            partitionNumber = x // chordPartitionSize
            hlsPartitions[partitionNumber] += np.array(hls + (1,))
            # print(f'{r}, {g}, {b} => {tempFromRGB(r, g, b)}')
            # print(totalWarmth / totalCount)

    for entry in hlsPartitions:
        entry /= entry[3]

    averageWarmth = (1 - totalWarmth / totalCount / 10000)      # -> tempo, tonality
    averageHue = totalHLS[0] / totalCount                       # -> tonality
    averageLuminance = totalHLS[1] / totalCount                 # -> tonality
    averageSaturation = totalHLS[2] / totalCount                # -> tempo

    tempo = averageWarmth * 0.3 + averageSaturation * 0.7
    isMajor = averageSaturation * 0.5 + averageLuminance * 0.5 > 0.5
    tonics = ['G#', 'D#', 'A#', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'C#']
    tonic = tonics[round(averageHue * 10)]

    tonicOpts = ["I", "VI", "III+", "i", "vi", "iii"]
    predominantOpts = ["IV", "iv", "iio"]
    dominantOpts = ["V", "viio"]

    chords = []

    for chord in range(len(hlsPartitions)):
        partition = hlsPartitions[chord]
        hue = partition[0]
        luminance = partition[1]
        saturation = partition[2]
        if chord == 0:
            tonicIdx = round(hue * 2)
            if not isMajor: tonicIdx += 3
            chords.append(tonicOpts[tonicIdx])
        elif chord == 1:
            if luminance > 0.7 and saturation < 0.3:  # foggy/gray = jazzy
                chords.append('iio')
            elif isMajor:
                chords.append('IV')
            else:
                chords.append('iv')
        elif chord == 2:
            if saturation > 0.6 and luminance < 0.3:  # dark + intense = viio
                chords.append('viio')
            else:
                chords.append('V')
        else:
            similarityToFirst = np.abs(partition - hlsPartitions[0])
            if similarityToFirst[0] < 0.2:
                chords.append(chords[0])
            else:
                start = 0 if isMajor else 3
                resolutionOptions = tonicOpts[start:start + 2]
                differentOpt = list(set(resolutionOptions) - set(chords[0]))[0]
                chords.append(differentOpt)

    print(chords)
    print(f'W: {averageWarmth}\tH: {averageHue}\tL: {averageLuminance}\tS: {averageSaturation}')

    cv2.imshow('test', im)
    cv2.waitKey(0)

    return {
        'image': im,
        'edges': edges,  # array of True/False indicating edges
        'tempo': tempo,
        'tonic': tonic,
        'chords': chords,
        'major': isMajor
    }
    # for row in result:
    #     for col in row:
    #         print('*' if col else '-', end='')
    #     print()

fetchTestImage()

# plt.subplot(121),plt.imshow(im,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges,cmap = 'gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
# plt.show()
#
# cv2.imshow('test', im)
# cv2.waitKey(0)
