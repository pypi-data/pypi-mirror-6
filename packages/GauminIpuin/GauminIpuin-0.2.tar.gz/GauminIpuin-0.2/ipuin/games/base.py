from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty

HELP = "Joku honek ez dauka laguntzarik."

EDITOR_HELP = "Joku honek ez dauka laguntzarik."

POPUP_KV = """#:kivy 1.0.9
<HelpPopup>:
    BoxLayout:
        orientation: "vertical"

        RstDocument:
            size_hint: 1, 0.9
            text: root.text

        Button:
            size_hint: 1, 0.1
            text: "Itxi"
            on_release: root.dismiss()
"""

GAME_KV = """#:kivy 1.0.9
<Game>:
    game_container: game_container
    BoxLayout:
        id: game_container
        orientation: "vertical"

        BoxLayout:
            id: box
            orientation: "horizontal"
            size_hint: 1, 0.1

            canvas.before:
                Color:
                    rgba: 0.75, 0.99, 0.27, 0.5

                Rectangle:
                    size: box.size
                    pos: box.pos

            Button:
                size_hint: 0.1, 1
                text: " ? "
                on_release: root.show_help()

            Label:
                size_hint: 0.9, 1
                color: 0,0,0,1
                text: root.description
"""

Builder.load_string(POPUP_KV)
Builder.load_string(GAME_KV)


class GameConfig(object):
    title = "Jokua"
    description = "Joku sinple bat"
    help_txt = EDITOR_HELP

    def __init__(self, ipuin, target):
        self.ipuin = ipuin
        self.target = target

    def build(self):
        return [
            Label(text=''),
            Label(text="Konfiguraziorik ez joku honentzat"),
        ]

    def save(self):
        pass

    def get_widgets(self):
        return [
            Label(text=self.description),
            Button(
                text='Laguntza',
                on_release=self.show_help
            ),
        ] + self.build()

    def show_help(self, button):
        popup = HelpPopup(title=self.title, text=self.help_txt)
        popup.open()


class HelpPopup(Popup):
    text = StringProperty(HELP)

    def __init__(self, *args, **kwargs):
        super(HelpPopup, self).__init__(*args, **kwargs)


class Game(Screen):
    kv_file = None
    config = GameConfig
    title = "Jokua"
    description = "Joku sinple bat"
    help_txt = HELP
    orientation = "vertical"

    def __init__(self, spec, *args, **kwargs):
        self.spec = spec
        self.register_event_type('on_game_exit')
        super(Game, self).__init__(*args, **kwargs)

        self.game_container.add_widget(self.build())

    def build(self):
        return Label(text="Joku hau momentuz ez dabil.")

    def on_game_exit(self, exitstep, *args):
        pass

    def exit(self, exitcode):
        self.dispatch('on_game_exit', self.spec[exitcode])

    def show_help(self):
        popup = HelpPopup(title=self.title, text=self.help_txt)
        popup.open()

    @classmethod
    def get_config(klass):
        return klass.config
