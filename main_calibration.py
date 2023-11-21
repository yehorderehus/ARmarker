import cv2
import numpy as np

class CameraCalibration:
    def __init__(self):
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    def calibrate(self, frame, aruco_corners, aruco_side_length):
        pass

        #return ret, dist, mtx, _, _
