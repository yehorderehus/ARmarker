import cv2
import numpy as np
import time


## Has to be written in future, for now just returns the predefined values
class CameraCalibration:
    def __init__(self) -> None:
        pass

    def calibrate(self):
        # Predefined distortion parameters for normal lenses
        k1 = -0.1
        k2 = 0.01
        p1 = 0.001
        p2 = 0.002

        # Focal lengths and principal point (you may need to adjust these based on your specific camera)
        fx = 800.0
        fy = 800.0
        cx = 640.0
        cy = 480.0

        # Create the camera matrix
        mtx = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ], dtype=np.float64)

        # Create the distortion coefficients
        dist = np.array([k1, k2, p1, p2, 0], dtype=np.float64)
        
        return None, dist, mtx, None, None
        # return ret, dist, mtx, rvecs, tvecs


"""  Chaotic drafts
class CameraCalibration:
    def __init__(self):
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.objpoints = []  # 3D points in real world space
        self.imgpoints = []  # 2D points in image plane

        self.max_frames = 50
        self.frame_count = 0

    def add_frame(self, frame, marker_corners, marker_size):
        #corners2 = cv2.cornerSubPix(np.float32(frame), np.float32(marker_corners), (11, 11), (-1, -1), self.criteria)
        #objp = np.array([[0, 0, 0], [marker_size, 0, 0], [0, marker_size, 0], [marker_size, marker_size, 0]], dtype=np.float32)
        objp = np.zeros((len(marker_corners), 3), dtype=np.float32)
        for i in range(len(marker_corners)):
            objp[i, :] = [marker_corners[i][0][0][0], marker_corners[i][0][0][1], 0]
        self.objpoints.append(objp)
        marker_corners = marker_corners[0]
        self.imgpoints.append(marker_corners.reshape(-1, 2)) # 4 are passed in but should only 1

    def calibrate(self, frame, marker_corners, marker_size):
        self.add_frame(frame, marker_corners, marker_size)
        self.frame_count += 1
        if self.frame_count == self.max_frames:
            self.frame_count -= 1
            time.sleep(0.1)
            self.imgpoints.pop(0)
            self.objpoints.pop(0)

        # Perform camera calibration
        height, width, _ = frame.shape
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, (width, height), None, None)
        return ret, dist, mtx, rvecs, tvecs
"""

#view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvecs[0]],
# [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvecs[1]],
# [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvecs[2]],
# [0.0 ,0.0 ,0.0 ,1.0 ]])

#view_matrix = view_matrix * self.INVERSE_MATRIX
#view_matrix = self.INVERSE_MATRIX

#view_matrix = np.transpose(view_matrix)

# load view matrix and draw shape
#glPushMatrix()
#glLoadMatrixd(view_matrix)
