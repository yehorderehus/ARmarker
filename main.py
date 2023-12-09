# Kivy and KivyMD imports
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

# Other imports
import webbrowser
import cv2
from plyer import filechooser

# Common imports
from main_helper import main_helper
from detection import MarkerDetection


class UserApp(MDApp):  # TODO optimization, work with memory
    def __init__(self) -> None:
        super().__init__()

        # Set supported extensions
        # TODO Most imread and videocapture extensions were NOT tested
        self.imread_extensions = [
            "bmp", "jpeg", "jpg", "jpe", "jp2",
            "png", "webp", "pbm", "pgm", "ppm",
            "pxm", "pnm", "sr", "ras", "tiff",
            "tif", "exr", "hdr", "pic"
        ]
        self.videocapture_extensions = [
            "gif", "mp4", "avi", "mov", "mkv",
            "wmv", "flv", "webm", "mpg", "mpeg",
            "ts", "m4v"
        ]
        self.opengl_extensions = ["obj"]

        # Initialize the marker detection class and pass supported extensions
        self.marker_detection = MarkerDetection(
            self.imread_extensions,
            self.videocapture_extensions,
            self.opengl_extensions
        )

        # Initialize variables
        self.cap_index = 0
        self.media_file, self.media_extension = None, None
        self.asset_file, self.asset_extension = None, None
        self.screen_width, self.screen_height = Window.size

        # Bind the resize event to update the screen size
        Window.bind(on_resize=lambda instance,
                    width, height: setattr(self, 'screen_width', width)
                    or setattr(self, 'screen_height', height))

        # Start execution by accessing the camera
        self.live_broadcast()

    def live_broadcast(self):
        if not cv2.VideoCapture(self.cap_index).isOpened():
            self.error_popup("Camera Error",
                             "Unable to access the camera. "
                             "Please check the camera connection.")
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
                    # Convert and update the live frame
                    self.root.ids.live_frame.texture = \
                        self.frame_to_texture(frame)

            # Update at specified FPS through kivy.clock
            self.update_live_event = Clock.schedule_interval(
                update_live, 1.0 / fps)

    def update_static_video(self, media=None):
        if not media:
            return

        # Open the video file and initialize a flag to control video looping
        self.cap_video = cv2.VideoCapture(media)
        self.video_loop = True

        # If 'fps' is not available in metadata, set a default frame rate
        try:
            fps = self.cap_video.get(cv2.CAP_PROP_FPS)
        except KeyError:
            fps = 30

        def update_video(dt):
            if hasattr(self, 'cap_video') and self.video_loop:
                ret, frame = self.cap_video.read()

                if ret:
                    # Convert and update the static frame
                    self.root.ids.static_frame.texture = \
                        self.frame_to_texture(frame)

                else:
                    # Video ended, release the video capture
                    self.cap_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Update at specified FPS through kivy.clock
        self.update_static_video_event = Clock.schedule_interval(
            update_video, 1.0 / fps)

    def update_static_image(self, media=None):
        if not media:
            return

        # Read the image from the file path
        frame = cv2.imread(media)

        # Convert and update the static frame
        self.root.ids.static_frame.texture = self.frame_to_texture(frame)

    def frame_to_texture(self, frame):
        # Process the frame and flip it vertically
        frame = self.marker_detection.process(
            frame, self.asset_file, self.asset_extension,
            self.screen_width, self.screen_height)
        frame = cv2.flip(frame, 0)

        # Convert the OpenCV frame to Kivy texture
        buf = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1],
                                       frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        return texture

    def file_select(self):
        file_path = filechooser.open_file()

        if not file_path:
            return None, None

        file_extension = file_path[0].split(".")[-1].lower()
        return file_path[0], file_extension

    def media_select_callback(self):
        self.media_file, self.media_extension = self.file_select()

        if self.media_file and self.media_extension:

            self.video_loop = False  # Stop looping

            if self.media_extension in self.imread_extensions:
                self.update_static_image(self.media_file)

            elif self.media_extension in self.videocapture_extensions:
                self.update_static_video(self.media_file)

            else:
                self.video_loop = True  # Continue looping if not supported
                self.error_popup("File Error", "Unsupported file type")

    def asset_select_callback(self):
        self.asset_file, self.asset_extension = self.file_select()

        if self.asset_file and self.asset_extension:

            self.video_loop = False  # Stop looping

            if (
                self.asset_extension in self.imread_extensions or
                self.asset_extension in self.videocapture_extensions
            ):
                if self.media_extension in self.imread_extensions:
                    self.update_static_image(self.media_file)
                elif self.media_extension in self.videocapture_extensions:
                    self.update_static_video(self.media_file)

            elif self.asset_extension in self.opengl_extensions:
                if self.media_extension in self.imread_extensions:
                    self.update_static_image(self.media_file)
                elif self.media_extension in self.videocapture_extensions:
                    self.update_static_video(self.media_file)

            else:
                self.video_loop = True  # Continue looping if not supported
                self.error_popup("File Error", "Unsupported file type")

    def model_rotate_callback(self):
        # Toggle model rotation
        pass

    def cam_flip_callback(self):
        # Switch between camera index 0 and 1
        if self.cap_index == 1:
            self.cap_index = 0
        else:
            self.cap_index = 1

        # Release and reopen the camera
        self.cap.release()
        self.live_broadcast()

    def change_screen_callback(self, current_screen):
        if current_screen != "live":
            if hasattr(self, "update_live_event"):
                self.cap.release()
                del self.update_live_event
        else:
            if not hasattr(self, 'update_live_event'):
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

    def open_url(self, url):
        webbrowser.open(url)

    class ContentNavigationDrawer(MDScrollView):
        screen_manager = ObjectProperty()
        nav_drawer = ObjectProperty()

    def build(self):
        self.title = "ARmarker tool"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "Gray"
        self.theme_cls.accent_hue = "500"

        return Builder.load_string(main_helper)


if __name__ == "__main__":
    UserApp().run()
