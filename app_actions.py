from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton


class AppActions:
    def __init__(self, app_instance, handler_instance) -> None:
        self.app_instance = app_instance
        self.handler_instance = handler_instance

    def start_live_broadcast(self, source):
        if self.handler_instance.init_cap(source, name="live") is False:
            self.error_popup(
                error_cause="Camera Error",
                error_message="Unable to access the camera. "
                "Please check if the camera is not being used by "
                "another application or the camera index is correct."
            )
            return

        def update_live(dt):
            if self.handler_instance.cap_check(name="live"):
                frame = self.handler_instance.refresh_cap(name="live")
                self.app_instance.root.ids.live_frame.texture = \
                    self.to_texture(frame)

        self.update_live_event = Clock.schedule_interval(
            update_live, 1.0 / self.handler_instance.get_fps(name="live"))

    def stop_live_broadcast(self):
        if hasattr(self, "update_live_event"):
            Clock.unschedule(self.update_live_event)
        self.handler_instance.cap_del(name="live")

    def static_display(self, format):
        if hasattr(self, "update_static_event"):
            Clock.unschedule(self.update_static_event)

        def update_static(dt):
            frame = self.handler_instance.get_video(type="media_output")
            self.app_instance.root.ids.static_frame.texture = \
                self.to_texture(frame)

        if format == "image":
            frame = self.handler_instance.get_image(type="media_output")
            self.app_instance.root.ids.static_frame.texture = \
                self.to_texture(frame)

        elif format == "video":
            self.update_static_event = Clock.schedule_interval(
                update_static, 1.0 / self.handler_instance.get_fps(
                    name="media_output"))

    def to_texture(self, frame):
        if frame is None:
            return None

        frame = self.handler_instance.frame_flip(frame)

        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(
            frame.tobytes(), colorfmt="bgr", bufferfmt="ubyte")
        return texture

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
