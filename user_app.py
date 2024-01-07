from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView

from app_helper import app_helper
from app_actions import AppActions
from handler import Handler

import webbrowser


class UserApp(MDApp):
    def __init__(self) -> None:
        super().__init__()

        self.handler = Handler()
        self.app_actions = AppActions(
            app_instance=self, handler_instance=self.handler)

        self.live_source = 0  # Default OpenCV camera index

    def build(self):
        self.title = "ARmarker tool"

        return Builder.load_string(app_helper)

    def on_start(self):
        self.app_actions.start_live_broadcast(self.live_source)

    def change_screen_callback(self, current_screen):
        if current_screen != "live":
            self.app_actions.stop_live_broadcast()

        elif current_screen == "live":
            self.app_actions.start_live_broadcast(self.live_source)

    def file_select_callback(self, type):
        if self.handler.select_file(type) is False:
            self.app_actions.error_popup(
                error_cause="File Error",
                error_message="Unable to access the file. "
                "Please check if the file exists \
                and the file extension is correct."
            )
            return

        format = self.handler.get_format()
        if format:
            self.app_actions.static_display(format)

    def model_rotate_callback(self):
        # TODO
        print("model_rotate_callback")

    def cam_flip_callback(self):
        self.live_source = self.handler.cam_flip(self.live_source)
        self.app_actions.live_broadcast(self.live_source)

    def cam_record_callback(self):
        # TODO
        print("cam_record_callback")

    def open_url_callback(self, url):
        webbrowser.open(url)


class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


if __name__ == "__main__":
    UserApp().run()
