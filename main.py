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
import cv2
import webbrowser
from plyer import filechooser

# Common imports
from main_helper import main_helper
from detection import MarkerDetection

class UserApp(MDApp):
    def __init__(self) -> None:
        super().__init__()

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
            fps = self.get_fps(self.cap)

            def update_live(dt):
                ret, frame = self.cap.read()

                if ret:
                    self.root.ids.live_frame.texture = \
                        self.frame_to_texture(frame)

            if hasattr(self, 'cap') and self.cap.isOpened():
                self.update_live_event = Clock.schedule_interval(
                    update_live, 1.0 / fps)

    def update_static_video(self):
        if not self.media_file:
            return

        self.cap_video = cv2.VideoCapture(self.media_file)
        fps = self.get_fps(self.cap_video)

        def update_video(dt):
            ret, frame = self.cap_video.read()

            if ret:
                self.root.ids.static_frame.texture = \
                    self.frame_to_texture(frame)
            else:
                self.cap_video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        if hasattr(self, 'cap_video'):
            self.update_static_video_event = Clock.schedule_interval(
                update_video, 1.0 / fps)

    def update_static_image(self):
        if not self.media_file:
            return
        
        if hasattr(self, 'update_static_video_event'):
            self.cap_video.release()
            Clock.unschedule(self.update_static_video_event)

        frame = cv2.imread(self.media_file)
        self.root.ids.static_frame.texture = self.frame_to_texture(frame)

    def frame_to_texture(self, frame):
        frame = self.marker_detection.process(
            frame, self.asset_file, self.asset_extension,
            self.screen_width, self.screen_height)
        frame = cv2.flip(frame, 0)

        # Convert the OpenCV frame to Kivy texture
        buf = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1],
                                       frame.shape[0]),
                                       colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        return texture

    def file_select(self):
        file_path = filechooser.open_file()

        if not file_path:
            self.error_popup("File Error", "No file selected")
            del file_path
            return None, None

        file_extension = file_path[0].split(".")[-1].lower()        
        
        return file_path[0], file_extension

    def media_select_callback(self):
        self.media_file, self.media_extension = self.file_select()

        if self.media_extension not in self.imread_extensions + \
            self.videocapture_extensions \
            and self.media_extension is not None:
                self.error_popup("File Error", "Unsupported file type")
                del self.media_file, self.media_extension
                return 

        self.update_static()

    def asset_select_callback(self):
        self.asset_file, self.asset_extension = self.file_select()

        if self.asset_extension not in self.imread_extensions + \
            self.videocapture_extensions + self.opengl_extensions \
            and self.asset_extension is not None:
                self.error_popup("File Error", "Unsupported file type")
                del self.asset_file, self.asset_extension
                return

        if self.asset_extension in self.imread_extensions:
            self.asset_file = cv2.imread(self.asset_file)

        elif self.asset_extension in self.videocapture_extensions:
            if hasattr(self, 'cap_asset'):
                self.cap_asset.release()
                Clock.unschedule(self.update_video_augment_event)

            self.cap_asset = cv2.VideoCapture(self.asset_file)
            fps = self.get_fps(self.cap_asset)

            def update_video_augment(dt):
                ret, frame = self.cap_asset.read()

                if ret:
                    self.asset_file = frame
                    if not hasattr(self, 'cap_video') and \
                        not hasattr(self, 'cap'):
                            self.update_static()
                else:
                    self.cap_asset.set(cv2.CAP_PROP_POS_FRAMES, 0)

            if self.cap_asset.isOpened():
                self.update_video_augment_event = Clock.schedule_interval(
                    update_video_augment, 1.0 / fps)

        elif self.asset_extension in self.opengl_extensions:
            # TODO Load the model
            pass
        
        self.update_static()

    def update_static(self):
        if self.media_extension in self.imread_extensions:
            self.update_static_image()

        elif self.media_extension in self.videocapture_extensions:
            self.update_static_video()
    
    def get_fps(self, cap):
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
        except KeyError:
            fps = 30

        return fps

    def model_rotate_callback(self):
        # TODO Toggle model rotation
        pass

    def cam_flip_callback(self):
        if self.cap_index == 1:
            self.cap_index = 0
        else:
            self.cap_index = 1

        self.cap.release()
        self.live_broadcast()

    # TODO more, for optimization
    def change_screen_callback(self, current_screen):
        if current_screen != "live" and hasattr(self, 'cap'):
            del self.cap
            Clock.unschedule(self.update_live_event)

        elif current_screen == "live":
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
