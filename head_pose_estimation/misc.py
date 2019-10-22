"""
Miscellaneous functions implemented by me.
"""

import numpy as np
import cv2

def eye_aspect_ratio(eye):
    """
    eye: array of shape 6x2
    """
    ear = np.linalg.norm(eye[1]-eye[5]) + np.linalg.norm(eye[2]-eye[4])
    ear/= (2*np.linalg.norm(eye[0]-eye[3])+1e-6)
    return ear

def mouth_aspect_ration(mouth):
    mar = np.linalg.norm(mouth[1]-mouth[7]) + np.linalg.norm(mouth[2]-mouth[6]) + np.linalg.norm(mouth[3]-mouth[5])
    mar/= (2*np.linalg.norm(mouth[0]-mouth[4])+1e-6)
    return mar

def mouth_distance(mouth):
    return np.linalg.norm(mouth[0]-mouth[4])

def detect_iris(frame, marks, side='left'):
    """
    return:
       x: the x coordinate of the iris.
       y: the y coordinate of the iris.
       x_rate: how much the iris is toward the left. 0 means totally left and 1 is totally right.
       y_rate: how much the iris is toward the top. 0 means totally top and 1 is totally bottom.
    """
    mask = np.full(frame.shape[:2], 255, np.uint8)
    if side == 'left':
        region = marks[36:42].astype(np.int32)
    elif side == 'right':
        region = marks[42:48].astype(np.int32)
    try:
        cv2.fillPoly(mask, [region], (0, 0, 0))
        eye = cv2.bitwise_not(frame, frame.copy(), mask=mask)
        # Cropping on the eye
        margin = 4
        min_x = np.min(region[:, 0]) - margin
        max_x = np.max(region[:, 0]) + margin
        min_y = np.min(region[:, 1]) - margin
        max_y = np.max(region[:, 1]) + margin

        eye = eye[min_y:max_y, min_x:max_x]
        eye = cv2.cvtColor(eye, cv2.COLOR_RGB2GRAY)

        eye_binarized = cv2.threshold(eye, np.quantile(eye, 0.2), 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(eye_binarized, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea)
        moments = cv2.moments(contours[-2])
        x = int(moments['m10'] / moments['m00']) + min_x
        y = int(moments['m01'] / moments['m00']) + min_y
        return x, y, (x-min_x-margin)/(max_x-min_x-2*margin), (y-min_y-margin)/(max_y-min_y-2*margin)
    except:
        return 0, 0, 0.5, 0.5

def shape_to_np(shape):
    coords = np.zeros((68, 2))
    for i in range(68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords