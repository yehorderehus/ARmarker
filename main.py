# Kivy and KivyMD imports
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

# Other imports
import cv2
import numpy as np
import webbrowser
from PIL import Image
from plyer import filechooser
from threading import Thread

# Common imports
from main_helper import main_helper
from main_calibration import CameraCalibration


class ARmarkerEngine:
    def __init__(self, supported_imread_extensions,
                 supported_videocapture_extensions,
                 supported_opengl_extensions):

        # Setup aruco
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

        # Import supported extensions from UserApp
        self.supported_imread_extensions = supported_imread_extensions
        self.supported_videocapture_extensions = supported_videocapture_extensions
        self.supported_opengl_extensions = supported_opengl_extensions

        # Initialize calibration
        self.calibration_thread = None

    def calibration(self, frame, arucoCorners, aruco_side_length):
        if self.calibration_thread and self.calibration_thread.is_alive():
            # Calibration is already in progress, don't start a new thread
            return
        
        def calibrate_in_thread(self, frame, arucoCorners, aruco_side_length):
            _, self.dist, self.mtx, _, _ = CameraCalibration().calibrate(frame, arucoCorners, aruco_side_length) 

        # Start calibration in a separate thread
        self.calibration_thread = Thread(target=calibrate_in_thread, args=(frame, arucoCorners, aruco_side_length))
        self.calibration_thread.start()

    def process(self, frame, object, object_type, object_extension):  # The receiving function
        return self.aruco_processing(frame, object, object_type, object_extension)
    
    def aruco_processing(self, frame, object, object_type, object_extension):
        processed_frame = frame.copy()  # Copy the frame to avoid mixing up

        # Loop through aruco dictionaries and aruco corners, apply augmentation
        for arucoDict in self.aruco_dictionaries:
            self.aruco_detection(frame, arucoDict)

            # 4 loops for 4 corners
            for arucoCorner in self.arucoCorners:
                if object_type == "plain":
                    if object_extension in self.supported_imread_extensions:
                        augment = cv2.imread(object)
                        processed_frame = self.plain_augmentation(arucoCorner, processed_frame, augment)

                    elif object_extension in self.supported_videocapture_extensions:  ## to work later - full length video augmentation
                        _, augment = cv2.VideoCapture(object).read()
                        processed_frame = self.plain_augmentation(arucoCorner, processed_frame, augment)

                elif object_type == "volumetric":
                    processed_frame = self.volumetric_augmentation(arucoCorner, processed_frame, augment)

                else:
                    processed_frame = self.aruco_highlightning(processed_frame, arucoCorner)
                    
        return processed_frame
    
    def aruco_detection(self, frame, arucoDict):
        self.arucoCorners, self.arucoIds, _ = cv2.aruco.detectMarkers(frame, cv2.aruco.getPredefinedDictionary(arucoDict), parameters=self.arucoParams)

        if self.arucoIds is not None:
            self.aruco_parameters(frame)

    def aruco_parameters(self, frame):
        for arucoCorner in self.arucoCorners:
            np_aruco_corners = self.aruco_np_corners(arucoCorner)

        self.aruco_side_length = int(np.linalg.norm(np_aruco_corners[0] - np_aruco_corners[1]))

        #for arucoId in range(len(self.arucoIds)):
            # Update calibration
            #self.calibration(frame, self.arucoCorners, self.aruco_side_length)
            #self.rvec, self.tvec, _ = cv2.aruco.estimatePoseSingleMarkers(self.arucoCorners[arucoId], 0.05, self.mtx, self.dist)

    def aruco_np_corners(self, arucoCorner):
        return np.int32(arucoCorner).reshape(-1, 2)
  
    def aruco_highlightning(self, processed_frame, arucoCorner):
        processed_frame = cv2.polylines(
        processed_frame,
        [self.aruco_np_corners(arucoCorner)],
        isClosed=True,
        color=(0, 255, 0),
        thickness=int(self.aruco_side_length * 0.01)  # Second parameter is the thickness ratio
        )

        return processed_frame

    def plain_augmentation(self, bbox, shot, augment):
        top_left = bbox[0][0][0], bbox[0][0][1]
        top_right = bbox[0][1][0], bbox[0][1][1]
        bottom_right = bbox[0][2][0], bbox[0][2][1]
        bottom_left = bbox[0][3][0], bbox[0][3][1]

        # Open an rectangular from augment and get its dimensions
        rectangle = Image.fromarray(augment)
        width, height = rectangle.size
        side_length = max(width, height)

        # Calculate position for centering the rectangular on a background
        x_offset = (side_length - width) // 2
        y_offset = (side_length - height) // 2

        # Make the background and paste the rectangular onto it
        background = Image.new("RGB", (side_length, side_length), (0, 0, 0))
        background.paste(rectangle, (x_offset, y_offset))

        # Convert edited augment to numpy array
        augment = np.array(background)

        # Find numpy arrays of the corner points of the shot and the augment
        points_shot = np.array([top_left, top_right, bottom_right, bottom_left])
        points_augment = np.array([[0, 0], [side_length, 0], [side_length, side_length], [0, side_length]])

        # Calculate the transformation matrix and warp the augment, fill the shot with the processed augment
        matrix = cv2.getPerspectiveTransform(points_augment.astype(np.float32), points_shot.astype(np.float32))
        augment = cv2.warpPerspective(augment, matrix, (shot.shape[1], shot.shape[0]))
        cv2.fillConvexPoly(shot, points_shot.astype(int), (0, 0, 0), 16)

        return shot + augment

    def volumetric_augmentation(self):  # to be implemented
        pass


class UserApp(MDApp):
    class ContentNavigationDrawer(MDScrollView):
        screen_manager = ObjectProperty()
        nav_drawer = ObjectProperty()

    def live_broadcast(self):
        if not cv2.VideoCapture(self.cap_index).isOpened():
            self.error_popup("Camera Error", "Unable to access the camera. Please check the camera connection.")
            self.root.ids.live_frame.texture = None
        else:
            self.cap = cv2.VideoCapture(self.cap_index)

            # If 'fps' is not available in metadata, set a default frame rate
            try:
                fps = self.cap.get(cv2.CAP_PROP_FPS)
            except KeyError:
                fps = 30

            def update_live(dt):
                ret, frame = self.cap.read()

                if ret:
                    # Convert and update
                    texture = self.frame_to_texture(frame)
                    self.root.ids.live_frame.texture = texture

            self.update_live_event = Clock.schedule_interval(update_live, 1.0 / fps)  # Update at specified FPS through kivy.clock

    def update_static_video(self, media=None):
        if not media:
            return

        # Open the video file and initialize a flag to control video looping
        self.cap_video = cv2.VideoCapture(media[0])
        self.video_loop = True

        # If 'fps' is not available in metadata, set a default frame rate
        try:
            fps = self.cap_video.get(cv2.CAP_PROP_FPS)
        except KeyError:
            fps = 30

        def update_video(dt):
            if hasattr(self, 'cap_video') and self.cap_video.isOpened() and self.video_loop:
                ret, frame = self.cap_video.read()

                if ret:
                    # Convert and update
                    texture = self.frame_to_texture(frame)
                    self.root.ids.static_frame.texture = texture

                else:
                    # Video ended, release the video capture
                    self.cap_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.update_static_video_event = Clock.schedule_interval(update_video, 1.0 / fps)  # Update at specified FPS through kivy.clock

    def update_static_image(self, media=None):
        if not media:
            return

        # Read the image from the file path
        frame = cv2.imread(media[0])

        # Convert and update
        texture = self.frame_to_texture(frame)
        self.root.ids.static_frame.texture = texture

    def frame_to_texture(self, frame):        

        # First process and THEN flip
        frame = self.ar_marker_engine.process(frame, self.object, self.object_type, self.object_extension)
        frame = cv2.flip(frame, 0)

        # Convert the OpenCV frame to Kivy texture
        buf = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        return texture

    def mediaselect_callback(self):
        media_selection = self.fileselect()

        if media_selection is not None:
            self.media_path, self.media_extension = media_selection

            self.video_loop = False  # Stop looping

            if self.media_extension in self.supported_videocapture_extensions:
                self.update_static_video(self.media_path)

            elif self.media_extension in self.supported_imread_extensions:
                self.update_static_image(self.media_path)

            else:
                self.error_popup("File Error", "Unsupported file type")
                self.video_loop = True  # Continue looping if not supported

    def objselect_callback(self):
        object_selection = self.fileselect()

        if object_selection is not None:
            object_path, self.object_extension = object_selection

            self.video_loop = False  # Stop looping

            if self.object_extension in self.supported_imread_extensions or self.object_extension in self.supported_videocapture_extensions:
                self.object = object_path[0]
                self.object_type = "plain"

                if self.media_extension in self.supported_imread_extensions:
                    self.update_static_image(self.media_path)
                elif self.media_extension in self.supported_videocapture_extensions:
                    self.update_static_video(self.media_path)

            elif self.object_extension in self.supported_opengl_extensions:
                self.object = object_path[0]
                self.object_type = "volumetric"

                if self.media_extension in self.supported_imread_extensions:
                    self.update_static_image(self.media_path)
                elif self.media_extension in self.supported_videocapture_extensions:
                    self.update_static_video(self.media_path)

            else:
                self.error_popup("File Error", "No file selected")
                self.video_loop = True  # Continue looping if not supported

    def fileselect(self):
        file_path = filechooser.open_file()

        if not file_path:
            return

        file_extension = file_path[0].split(".")[-1].lower()
        return file_path, file_extension

    def objrotate_callback(self):
        # call the object rotate function from ARmarkerEngine
        pass

    def camrecord_callback(self):
        # click for screenshot, hold for video
        pass

    def camrotate_callback(self):
        # Switch between camera index 0 and 1
        if self.cap_index == 1:
            self.cap_index = 0
        else:
            self.cap_index = 1

        # Release and reopen the camera
        self.cap.release()
        self.live_broadcast()

    def error_popup(self, error_cause, error_message):
        dialog = MDDialog(
            title=f"{error_cause}",
            text=f"{error_message}",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda *x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def change_screen(self, screen_name):  # experimental, for handling screen output displaying
        current_screen = screen_name
        if current_screen != "live":
            if hasattr(self, "update_live_event"):
                self.cap.release()
                del self.update_live_event
        else:
            if not hasattr(self, 'update_live_event'):
                self.live_broadcast()

        if current_screen != "static":
            pass
        else:
            pass

    def open_url(self, url):
        webbrowser.open(url)

    def build(self):
        self.title = "ARmarker tool"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"

        # Initialize camera capture
        self.cap_index = 0
        self.live_broadcast()

        # Define events
        # part of experimental screen output handling
        self.update_static_gif_event = None
        self.update_static_video_event = None

        # Set supported extensions
        self.supported_imread_extensions = ["bmp", "jpeg", "jpg", "jpe", "jp2", "png", "webp", "pbm", "pgm", "ppm", "pxm", "pnm", "sr", "ras", "tiff", "tif", "exr", "hdr", "pic"]
        self.supported_videocapture_extensions = ["gif", "mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "mpg", "mpeg", "ts", "m4v"]
        self.supported_opengl_extensions = ["obj"] ## most imread and videocapture extensions were not tested!

        # Initialize ARmarkerEngine and pass supported extensions
        self.ar_marker_engine = ARmarkerEngine(self.supported_imread_extensions, self.supported_videocapture_extensions, self.supported_opengl_extensions)

        # Set initial values
        self.object = None
        self.object_type = None
        self.object_extension = None
        self.media_path = None
        self.media_extension = None

        return Builder.load_string(main_helper)


if __name__ == "__main__":
    UserApp().run()