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

# ARmarkerEngine imports
import cv2

class ARmarkerEngine:
    # implement here
    pass

class UserApp(MDApp):
    class ContentNavigationDrawer(MDScrollView):
        screen_manager = ObjectProperty()
        nav_drawer = ObjectProperty()

    def opencv_broadcast(self):
        # Check camera availability
        if not cv2.VideoCapture(self.opencv_cap_index).isOpened():
            self.camera_error_popup()
            self.root.ids.opencv_stream.texture = None
        else:
            self.cap = cv2.VideoCapture(self.opencv_cap_index)
            def update_frame(dt):
                ret, frame = self.cap.read()

                if ret:
                    # Convert the OpenCV frame to Kivy texture
                    buf1 = cv2.flip(frame, 0)
                    buf = buf1.tostring()
                    texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
                    texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

                    # Update the Image widget with the new frame
                    self.root.ids.opencv_stream.texture = texture

            Clock.schedule_interval(update_frame, 1.0 / 30.0)  # Update at 30 FPS

    def camera_error_popup(self):
        dialog = MDDialog(
            title="Camera Error",
            text="Unable to access the camera. Please check the camera connection.",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda *x: dialog.dismiss()
                )
            ]
        )
        dialog.open()        

    def objrotate_callback(self):
        pass

    def objselect_callback(self):
        pass

    def camrecord_callback(self):
        pass

    def camrotate_callback(self):
        # Switch between camera index 0 and 1
        if self.opencv_cap_index == 1:
            self.opencv_cap_index = 0
        else:
            self.opencv_cap_index = 1

        # Release the current camera capture
        self.cap.release()

        # Reopen the new camera capture
        self.opencv_broadcast()

    def build(self):
        self.title = "ARmarker tool"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"

        # Initialize camera
        self.opencv_cap_index = 0
        self.opencv_broadcast()
        
        return Builder.load_string(main_helper)

if __name__ == "__main__":
    UserApp().run()
