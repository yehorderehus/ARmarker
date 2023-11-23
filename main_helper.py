main_helper = """
<ContentNavigationDrawer>:
    MDList:
        spacing: "12dp"
        OneLineListItem:
            text: "Live Replacement"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "live"
                app.change_screen_callback("live")
        OneLineListItem:
            text: "Replace on Media"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "static"
                app.change_screen_callback("static")
        OneLineListItem:
            text: "Gallery"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "captures"
                app.change_screen_callback("captures")
        OneLineListItem:
            text: "3D Models"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "models"
                app.change_screen_callback("models")
        OneLineListItem:
            text: "ARmarkers"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "markers"
                app.change_screen_callback("markers")
        OneLineListItem:
            text: "About"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "about"
                app.change_screen_callback("about")
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: self.minimum_height
            OneLineListItem:
                text: "Git Wiki"
                divider: None
                theme_text_color: "Secondary"
                on_press:
                    root.nav_drawer.set_state("close")
                    app.open_url("# to set")
            OneLineListItem:
                text: "Rate App"
                divider: None
                theme_text_color: "Secondary"
                on_press:
                    root.nav_drawer.set_state("close")
                    app.open_url("# to set") 
MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            id: screen_manager
            MDScreen:
                name: "live"
                Image:
                    id: live_frame
                    allow_stretch: True
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state("open")
                MDIconButton:
                    icon: "rotate-360"
                    pos_hint: {"top": 1, "right": 1}
                    on_release: app.model_rotate_callback()
                MDIconButton:
                    icon: "cube-outline"
                    pos_hint: {"bottom": 1}
                    on_release: app.asset_select_callback()
                MDIconButton:
                    icon: "record"
                    pos_hint: {"bottom": 1, "center_x": .5}
                    on_release: app.cam_record_callback()
                MDIconButton:
                    icon: "rotate-3d-variant"
                    pos_hint: {"bottom": 1, "right": 1}
                    on_release: app.cam_flip_callback()
            MDScreen:
                name: "static"
                Image:
                    id: static_frame
                    allow_stretch: True
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
                MDIconButton:
                    icon: "rotate-360"
                    pos_hint: {"top": 1, "right": 1}
                    on_release: app.model_rotate_callback()
                MDIconButton:
                    icon: "cube-outline"
                    pos_hint: {"bottom": 1}
                    on_release: app.asset_select_callback()
                MDIconButton:
                    icon: "record"
                    pos_hint: {"bottom": 1, "center_x": .5}
                    on_release: app.cam_record_callback()
                MDIconButton:
                    icon: "file-image-plus"
                    pos_hint: {"bottom": 1, "right": 1}
                    on_release: app.media_select_callback()
            MDScreen:
                name: "captures"
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
            MDScreen:
                name: "models"
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
            MDScreen:
                name: "markers"
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
            MDScreen:
                name: "about"
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
        MDNavigationDrawer:
            id: nav_drawer
            MDBoxLayout:
                orientation: "vertical"
                padding: "12dp"
                spacing: "12dp"
                MDNavigationDrawerHeader:
                    title: "ARmarker tool"
                    padding: "16dp"
                    font_style: "Overline"
                ContentNavigationDrawer:
                    screen_manager: screen_manager
                    nav_drawer: nav_drawer
"""