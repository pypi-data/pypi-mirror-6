from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder

import json

from games import registered_games
from games import choose_one, reorder, riddle, connect, mark_correct, reorder_sentences


Builder.load_string("""

<GameTester>:
    orientation: "vertical"

    Label:
        text: root.title
        size_hint: 1, 0.1

    Button:
        text: "Bukatu"
        size_hint: 1, 0.1
        on_release: app.stop()
""")

GAMEDATA = {
    'ChooseOne': {"exit1": "step3", "exit2": "step4"},
    'Reorder': {"exit": "step2", "answers": ["Marko", "Panpin", "Ilargia"]},
    'Riddle': {"exit": "step2", "question": "Zenbat begi ditu Markok", "answers": ["bat", "1"]},
    'Connect': {"exit": "step2", "items": {'bat': '1', 'bi': '2', 'hiru': '3'}},
    'MarkCorrect': {"exit": "step2", "choices": [["bat", True], ["bi", False], ["hiru", True], ["lau", False]]},
    'ReorderSentences': {"exit": "step2", "sentences": ["1 - Marko", "2 - Panpin", "3 - Ilargia"]},
}


class GameTester(BoxLayout):
    title = StringProperty('')


class GameTesterApp(App):
    def __init__(self, gamename, spec, *args, **kwargs):
        super(GameTesterApp, self).__init__(*args, **kwargs)

        self.gamename = gamename

        Game = registered_games[gamename]
        self.game = Game(spec, name="game")
        self.game.bind(on_game_exit=self.on_game_exit)

    def build(self):
        root = GameTester(title=self.gamename)
        root.add_widget(self.game)
        return root

    def on_game_exit(self, instance, stepname):
        print "exit!: %s" % stepname


def main(gamename, spec,):
    GameTesterApp(gamename, spec).run()


if __name__ == '__main__':
    import sys
    gamename = sys.argv[1]
    if len(sys.argv) >> 2:
        spec = json.loads(sys.argv[2])
    elif gamename in GAMEDATA:
        spec = GAMEDATA[gamename]
    else:
        spec = {}
    main(gamename, spec)
