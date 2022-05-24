import cv2
import pandas as pd
import numpy as np
import sklearn
import seaborn as sns
import numpy as np
import math
import timeit
from queue import Queue

class Drive:
    frame = 0
    yellow_detected = Queue(maxsize=5)
    left_detected = Queue(maxsize=5)
    right_detected = Queue(maxsize=5)

    def __init__():
        yellow_detected.put(1)
        left_detected.put(1)
        right_detected.put(1)
        yellow_sum = 0
        left_sum = 0
        right_sum = 0

    def valueComputation(yellow, left, right):
        if frame <= 4:
            yellow_detected.put(yellow)
            yellow_sum += yellow

            left_detected.put(left)
            left_sum += left

            right_detected.put(right)
            right_sum += right
        else:
            yellow_sum -= yellow_detected.get()
            yellow_detected.put(yellow)
            yellow_sum += yellow

            left_sum -= left_detected.get()
            left_detected.put(left)
            left_sum += left

            right_sum -= right_detected.get()
            right_detected.put(right)
            right_sum += right

    def drivingStrategy(self):
        # still initialising, drive straight
        if frame <= 4:
            how = 'centre'

        # driving at the centre, take left
        elif yellow_sum >= 4 and left_sum >= 4 and right_sum >= 4:
            how = 'left'

        # at the left half of the track, drive straight from now
        elif yellow_sum >= 3 and left_sum >= 3 and right_sum <= 3:
            how = 'leftcentre'

        # right turn

        # time to take a right
        elif yellow_sum <= 2 and left_sum >= 4:
            how = 'right'
        # turn taken, drive straight from now
        elif yellow_sum >= 3  and left_sum >= 3:
            how = 'leftcentre'

        # left turn

        # time to take a left
        elif yellow_sum >= 4 and left_sum <= 2:
            how = 'left'
        # turn taken, drive straight from now
        elif yellow_sum >= 3 and left_sum >= 3:
            how = 'leftcentre'

        return how

    def direction(image):
        central_missing = 0

        # centre
        height, width, channels = image.shape
        croppedImage = image[int(height / 2):height, 0:width]
        grayImage = cv2.cvtColor(croppedImage, cv2.COLOR_BGR2GRAY)
        ret, yellowLine = cv2.threshold(grayImage, 200, 255, cv2.THRESH_BINARY)
        yellowBlur = cv2.GaussianBlur(yellowLine, (5, 5), 0)
        yellowEdges = cv2.Canny(yellowBlur, 200, 255)
        try:
            yellow_line_segments = detect_line_segments(yellowEdges)
            central_angle = steeringAngle(yellow_line_segments, height, width)
            yellow_detected = 1
        except:
            central_missing = 1

        # left
        ret, bothLines = cv2.threshold(grayImage, 100, 255, cv2.THRESH_BINARY)
        whiteLine = bothLines - yellowLine
        mask = np.zeros((240, 640), dtype='uint8')
        rect = cv2.rectangle(mask, (0, height), (int(0.5 * width / 3), 0), (1, 1, 1), -1)
        whiteLineLeft = cv2.bitwise_and(whiteLine, whiteLine, mask=rect)
        whiteLeftBlur = cv2.GaussianBlur(whiteLineLeft, (5, 5), 0)
        whiteLeftEdges = cv2.Canny(whiteLeftBlur, 200, 255)
        white_left_line_segments = detect_line_segments(whiteLeftEdges)
        try:
            left_angle = steeringAngle(white_left_line_segments, height, width)
            left_detected = 1
        except:
            left_detected = 0

        # right
        ret, bothLines = cv2.threshold(grayImage, 100, 255, cv2.THRESH_BINARY)
        whiteLine = bothLines - yellowLine
        mask = np.zeros((240, 640), dtype='uint8')
        rect = cv2.rectangle(mask, (int(2.5 * width / 3), height), (width, 0), (1, 1, 1), -1)
        whiteLineRight = cv2.bitwise_and(whiteLine, whiteLine, mask=rect)
        whiteRightBlur = cv2.GaussianBlur(whiteLineRight, (5, 5), 0)
        whiteRightEdges = cv2.Canny(whiteRightBlur, 200, 255)
        white_right_line_segments = detect_line_segments(whiteRightEdges)
        try:
            right_angle = steeringAngle(white_right_line_segments, height, width)
            right_detected = 1
        except:
            right_detected = 0

        set_values(yellow_detected, left_detected, right_detected)
        return [central_angle, left_angle, right_angle]

    def driver(self):
        image = cv2.imread("currentFrame.png")
        angles = direction(image)
        logic = drivingStrategy()

        if logic == 'centre':
            try:
                return angles[0]
            except:
                return (angles[1] + angles[2]) / 2
        elif logic == 'left':
            return angles[1]

        elif logic == 'right':
            return angles[2]

        elif logic == 'leftcentre':
            return (angles[0] + angles[1]) / 2

        else:
            try:
                return angles[0]
            except:
                return (angles[1] + angles[2]) / 2