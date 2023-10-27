# Comments start with big letter, TO-DOs with small

# Kivy and KivyMD imports
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

# Helper import
from main_helper import main_helper

# Other imports
import cv2
import numpy as np
import webbrowser
import imageio
from PIL import Image
from plyer import filechooser
#from typing import Optional, overload, Tuple, List, Union # for probably further use

class ARmarkerEngine:
    def __init__(self):
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
        
    def process(self, frame, object, object_type): # this will be crossroad for aruco / orb
        self.aruco_detection(frame, object, object_type)

        return frame
    
    def aruco_detection(self, frame, object, object_type):
        # Loop through the aruco dictionaries
        for arucoDict in self.aruco_dictionaries:
            arucoCorners, arucoIds, arucoRejected = cv2.aruco.detectMarkers(frame, cv2.aruco.getPredefinedDictionary(arucoDict), parameters=self.arucoParams)
            
            if object_type == "plain":
                for arucoCorner in arucoCorners:
                    frame = self.plain_augmentation(arucoCorner, frame, object)
            elif object_type == "volumetric":
                for arucoCorner in arucoCorners:
                    frame = self.volumetric_augmentation(arucoCorner, frame, object)
            else:
                # If no object is selected, encircle the detected marker
                for corner in arucoCorners:
                    aruco_corners = np.int32(corner).reshape(-1, 2)

                    # Calculate the side length of the detected marker
                    aruco_side_length = int(np.linalg.norm(aruco_corners[0] - aruco_corners[1]))
                    polylines_thickness = int(aruco_side_length * 0.01) # Second parameter is the thickness ratio

                    # Draw the polygon around the detected marker
                    cv2.polylines(
                        frame,
                        [aruco_corners],
                        isClosed=True,
                        color=(0, 255, 0),
                        thickness=polylines_thickness
                    )

        return frame
    
    def plain_augmentation(self, bbox, shot, augment): # for now works with images only, will be updated for videos and gifs (videos and gifs augmentation for now crash the app!)
        top_left = bbox[0][0][0], bbox[0][0][1]
        top_right = bbox[0][1][0], bbox[0][1][1]
        bottom_right = bbox[0][2][0], bbox[0][2][1]
        bottom_left = bbox[0][3][0], bbox[0][3][1]
        
        # Open the rectangular from augment and get its dimensions
        rectangle = cv2.imread(augment)
        rectangle = Image.fromarray(rectangle)
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

        # test
        result = np.array(shot + augment)
        cv2.imshow("result", result)

        return shot + augment # Malevich marker problem - black background, only first aruco marker is processed; imshow shows the correct result

    def volumetric_augmentation(self):
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

            def update_live(dt):
                ret, frame = self.cap.read()

                if ret:
                    # Convert and update
                    texture = self.frame_to_texture(frame)
                    self.root.ids.live_frame.texture = texture  
            
            self.update_live_event = Clock.schedule_interval(update_live, 1.0 / 30.0) # Update at 30 FPS through kivy.clock

    def update_static_video(self, media=None):
        if not media:
            return
        
        # Open the video file and initialize a flag to control video looping
        self.cap_video = cv2.VideoCapture(media[0])
        self.video_loop = True

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

        self.update_static_video_event = Clock.schedule_interval(update_video, 1.0 / 30.0)  # Update at 30 FPS through kivy.clock

    def update_static_gif(self, media=None):
        if not media:
            return
        
        # Open the GIF file and get its frame rate
        gif_reader = imageio.get_reader(media[0])

        # If 'fps' is not available in metadata, set a default frame rate
        try:
            fps = gif_reader.get_meta_data()['fps']
        except KeyError:
            fps = 10

        # Create a list of frames to be processed
        frames = list(gif_reader)

        # Initialize the frame index and a flag to control GIF looping
        self.frame_index = 0
        self.gif_loop = True

        # Define a function to update the static frame
        def update_gif(dt):
            if self.gif_loop:
                if self.frame_index < len(frames):
                    frame = frames[self.frame_index]
                    
                    # Convert and update
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Especial color conversion for GIFs
                    texture = self.frame_to_texture(frame)
                    self.root.ids.static_frame.texture = texture
                    self.frame_index += 1
                else:
                    # Reset the frame index to loop the GIF
                    self.frame_index = 0

        self.update_static_gif_event = Clock.schedule_interval(update_gif, 1.0 / fps) # Update at specified FPS through kivy.clock 

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
        frame = ARmarkerEngine().process(frame, self.object, self.object_type)
        frame = cv2.flip(frame, 0)

        # Convert the OpenCV frame to Kivy texture
        buf = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        return texture   

    def mediaselect_callback(self):
        media_selection = self.fileselect()

        if media_selection is not None:
            self.media_path, self.media_extension = media_selection # Self because of object function

            self.gif_loop = self.video_loop = False  # Stop looping

            if self.media_extension == "gif":
                self.update_static_gif(self.media_path)
            elif self.media_extension in self.supported_videocapture_extensions:
                self.update_static_video(self.media_path)
            elif self.media_extension in self.supported_imread_extensions:
                self.update_static_image(self.media_path)
            else:
                self.error_popup("File Error", "Unsupported file type")
                self.gif_loop = self.video_loop = True  # Continue looping if not supported

    def objselect_callback(self):
        object_selection = self.fileselect()

        if object_selection is not None:
            object_path, object_extension = object_selection

            self.gif_loop = self.video_loop = False  # Stop looping

            if object_extension in self.supported_imread_extensions or object_extension in self.supported_videocapture_extensions or object_extension == "gif":
                self.object = object_path[0]
                self.object_type = "plain"

                # Check media type and update
                if self.media_extension in self.supported_imread_extensions:
                    self.update_static_image(self.media_path)
                elif self.media_extension in self.supported_videocapture_extensions:
                    self.update_static_video(self.media_path)
                elif self.media_extension == "gif":
                    self.update_static_gif(self.media_path)

            elif object_extension in self.supported_opengl_extensions:
                self.object = object_path[0]
                self.object_type = "plain"

                # Check media type and update
                if self.media_extension in self.supported_imread_extensions:
                    self.update_static_image(self.media_path)
                elif self.media_extension in self.supported_videocapture_extensions:
                    self.update_static_video(self.media_path)
                elif self.media_extension == "gif":
                    self.update_static_gif(self.media_path)        
            else:
                self.error_popup("File Error", "No file selected")
                self.gif_loop = self.video_loop = True  # Continue looping if not supported

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

    def change_screen(self, screen_name): # experimental, for handling screen output displaying
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
        self.supported_videocapture_extensions = ["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "mpg", "mpeg", "ts", "m4v"]
        self.supported_opengl_extensions = ["obj"]

        # Set initial values
        self.object = None
        self.object_type = None
        self.media_path = None
        self.media_extension = None
        
        return Builder.load_string(main_helper)
    
if __name__ == "__main__":
    UserApp().run()

