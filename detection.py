import cv2
import numpy as np

from augmentation import FrameAugmentation
from calibration import CameraCalibration


class MarkerDetection:
    def __init__(self, extensions) -> None:
        self.extensions = extensions

        self.arucoParams = cv2.aruco.DetectorParameters()
        self.aruco_dictionaries = [
            cv2.aruco.DICT_4X4_50,
            cv2.aruco.DICT_4X4_100,
            cv2.aruco.DICT_4X4_250,
            cv2.aruco.DICT_4X4_1000,
            cv2.aruco.DICT_5X5_50,
            cv2.aruco.DICT_5X5_100,
            cv2.aruco.DICT_5X5_250,
            cv2.aruco.DICT_5X5_1000,
            cv2.aruco.DICT_6X6_50,
            cv2.aruco.DICT_6X6_100,
            cv2.aruco.DICT_6X6_250,
            cv2.aruco.DICT_6X6_1000,
            cv2.aruco.DICT_7X7_50,
            cv2.aruco.DICT_7X7_100,
            cv2.aruco.DICT_7X7_250,
            cv2.aruco.DICT_7X7_1000,
            cv2.aruco.DICT_ARUCO_ORIGINAL,
            cv2.aruco.DICT_APRILTAG_16h5,
            cv2.aruco.DICT_APRILTAG_25h9,
            cv2.aruco.DICT_APRILTAG_36h10,
            cv2.aruco.DICT_APRILTAG_36h11
        ]

    # The receiving function
    # TODO ORB feature detection
    def process(self, frame, the_asset, asset_extension):
        return self.aruco_processing(frame, the_asset, asset_extension)

    def aruco_processing(self, frame, the_asset, asset_extension):
        processed_frame = frame.copy()  # Copy the frame to avoid mixing up

        for arucoDict in self.aruco_dictionaries:
            self.aruco_detection(frame, arucoDict)

            # 4 loops for 4 corners
            for arucoCorner in self.arucoCorners:
                if asset_extension in self.extensions["imread"] \
                    or asset_extension in self.extensions["videocapture"]:
                    processed_frame = FrameAugmentation().plain_augmentation(
                        arucoCorner, processed_frame, the_asset)

                elif asset_extension in self.extensions["opengl"]:
                    processed_frame = FrameAugmentation().model_augmentation(
                        arucoCorner, processed_frame, the_asset)

                else:
                    processed_frame = self.aruco_highlightning(
                        processed_frame, arucoCorner)

        return processed_frame

    def aruco_detection(self, frame, arucoDict):
        self.arucoCorners, self.arucoIds, _ = cv2.aruco.detectMarkers(
            frame, cv2.aruco.getPredefinedDictionary(arucoDict),
            parameters=self.arucoParams)

        if self.arucoIds is not None:
            self.aruco_properties()

    def aruco_np_corners(self, arucoCorner):
        return np.int32(arucoCorner).reshape(-1, 2)

    def aruco_properties(self):
        for arucoCorner in self.arucoCorners:
            np_aruco_corners = self.aruco_np_corners(arucoCorner)

        self.aruco_side_length = int(np.linalg.norm(
            np_aruco_corners[0] - np_aruco_corners[1]))

        for arucoId in range(len(self.arucoIds)):
            # Update calibration
            _, self.dist, self.mtx, _, _ = CameraCalibration().calibrate()
            self.rvec, self.tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                self.arucoCorners[arucoId], 0.05, self.mtx, self.dist)

    def aruco_highlightning(self, processed_frame, arucoCorner):
        processed_frame = cv2.polylines(
            processed_frame,
            [self.aruco_np_corners(arucoCorner)],
            isClosed=True,
            color=(0, 255, 0),
            # Second parameter is the thickness ratio
            thickness=int(self.aruco_side_length * 0.01)
        )

        return processed_frame
