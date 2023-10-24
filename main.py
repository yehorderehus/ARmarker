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
import webbrowser
from plyer import filechooser
#from typing import Optional, overload, Tuple, List, Union # for probably further use

class ARmarkerEngine:
    def live_processing(self, frame):
        return frame
    
    def static_processing(self, frame):
        return frame

class UserApp(MDApp):
    class ContentNavigationDrawer(MDScrollView):
        screen_manager = ObjectProperty()
        nav_drawer = ObjectProperty()

    def live_broadcast(self):
        if not cv2.VideoCapture(self.cap_index).isOpened():
            self.live_broadcast_error()
            self.root.ids.live_frame.texture = None
        else:
            self.cap = cv2.VideoCapture(self.cap_index)
            Clock.schedule_interval(self.update_live, 1.0 / 30.0) # Update at 30 FPS through kivy.clock    

    def update_live(self, dt):
        ret, frame = self.cap.read()
        frame = ARmarkerEngine().live_processing(frame)
    
        if ret:
            # Convert the OpenCV frame to Kivy texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            # Update the Image widget with the new frame
            self.root.ids.live_frame.texture = texture                  

    def upload_static_callback(self):
        file_path = filechooser.open_file(title="Select Media")

        if file_path:
            frame = cv2.imread(file_path[0])

            if frame is not None and frame.size > 0:
                # Flip the frame and process
                frame = cv2.flip(frame, 0) # 0 for vertical, 1 for horizontal
                frame = ARmarkerEngine().static_processing(frame)

                # Convert the OpenCV frame to Kivy texture
                buf = frame.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

                # Update the Image widget with the new frame
                self.root.ids.static_frame.texture = texture
            else:
                self.root.ids.static_frame.texture = None
                self.upload_static_error()
        else:
            # further implement pop-up if non media was selected
            pass

    def objrotate_callback(self):
        # call the object rotate function from ARmarkerEngine
        pass

    def objselect_callback(self):
        # object selection
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

    def live_broadcast_error(self):
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

    def upload_static_error(self):
        dialog = MDDialog(
            title="Media Loading Error",
            text="Failed to load the selected media. Please check the file format and try again.",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda *x: dialog.dismiss()
                )
            ]
    )
    
    def open_url(self, url):
        webbrowser.open(url)

    def build(self):
        self.title = "ARmarker tool"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"

        # Initialize camera
        self.cap_index = 0
        self.live_broadcast()
        
        return Builder.load_string(main_helper)

if __name__ == "__main__":
    UserApp().run()
