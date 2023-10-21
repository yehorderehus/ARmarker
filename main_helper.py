main_helper = """
<ContentNavigationDrawer>:
    MDList:
        MDLabel:
            text: "ARmarker tool"
            font_style: "H6"
            padding: "16dp"
        OneLineListItem:
            text: ""
            divider: None
        OneLineListItem:
            text: "Live Replacement"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "live"
        OneLineListItem:
            text: "static"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "static"
        OneLineListItem:
            text: "frames"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "frames"
        OneLineListItem:
            text: "objects"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "objects"
        OneLineListItem:
            text: "markers"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "markers"
        OneLineListItem:
            text: "about"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "about"
MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            id: screen_manager
            MDScreen:
                name: "live"
                Image:
                    id: opencv_stream
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
                    icon: "rotate-3d-variant"
                    pos_hint: {"bottom": 1, "right": 1}
                    on_release: app.camrotate_callback()
            MDScreen:
                name: "static"
                MDIconButton:
                    icon: "menu"
                    pos_hint: {"top": 1}
                    on_release: nav_drawer.set_state()
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
            ContentNavigationDrawer:
                screen_manager: screen_manager
                nav_drawer: nav_drawer
"""