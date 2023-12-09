import numpy as np


# TODO Has to be written in future, for now just returns the predefined values
class CameraCalibration:
    def __init__(self) -> None:
        pass

    # For normal lenses
    def calibrate(self):
        # Distortion parameters
        k1 = -0.1
        k2 = 0.01
        p1 = 0.001
        p2 = 0.002

        # Focal lengths and principal points
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
