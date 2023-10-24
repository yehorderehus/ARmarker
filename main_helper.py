main_helper = """
<ContentNavigationDrawer>:
    MDList:
        spacing: "12dp"
        OneLineListItem:
            text: "Live Replacement"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "live"
        OneLineListItem:
            text: "Replace on Media"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "static"
        OneLineListItem:
            text: "Gallery"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "frames"
        OneLineListItem:
            text: "Objects"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "objects"
        OneLineListItem:
            text: "ARmarkers"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "markers"
        OneLineListItem:
            text: "About"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "about"
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
                    on_release: app.objrotate_callback()
                MDIconButton:
                    icon: "cube-outline"
                    pos_hint: {"bottom": 1}
                    on_release: app.objselect_callback()
                MDIconButton:
                    icon: "record"
                    pos_hint: {"bottom": 1, "center_x": .5}
                    on_release: app.camrecord_callback()
                MDIconButton:
                    icon: "rotate-3d-variant"
                    pos_hint: {"bottom": 1, "right": 1}
                    on_release: app.camrotate_callback()
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
                    on_release: app.objrotate_callback()
                MDIconButton:
                    icon: "cube-outline"
                    pos_hint: {"bottom": 1}
                    on_release: app.objselect_callback()
                MDIconButton:
                    icon: "record"
                    pos_hint: {"bottom": 1, "center_x": .5}
                    on_release: app.camrecord_callback()
                MDIconButton:
                    icon: "file-image-plus"
                    pos_hint: {"bottom": 1, "right": 1}
                    on_release: app.upload_static_callback()
            MDScreen:
                name: "frames"
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
            MDScreen:
                name: "objects"
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