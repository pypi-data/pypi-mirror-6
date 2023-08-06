from . import register_game
from .base import Game, GameConfig
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from random import random

from ipuin.uix import StepSpinner

HELP = \
"""
Berrantolatu
============

Talde bakoitzean hizkiak lekuz mugitu dira!

Idatzi talde bakoitzaren azpian hitz berrantolatua.
"""

EDITOR_HELP = \
"""
Berrantolatu
============

Idatzi desordenatuta agertuko diren hitzak, bat lerro bakoitzean.
"""


class ReorderConfig(GameConfig):
    title = "Berrantolatu"
    description = "Asmatu ezkutuko hitza"
    help_txt = EDITOR_HELP

    def build(self):
        text = "\n".join(self.target.get('answers', []))
        self.answers = TextInput(text=text)
        self.exit = StepSpinner(
            key=self.target.get('exit', '---'),
            items=self.ipuin.steps,
        )

        return [
            Label(text='Erantzunak'),
            self.answers,
            Label(text='Helburua'),
            self.exit
        ]

    def save(self):
        self.target['answers'] = self.answers.text.split('\n')
        self.target['exit'] = self.exit.key
        self.target['target'] = 'Reorder'


class ShuffledLabel(Label):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.pos_hint = {}  # Ignore initial pos_hint, otherwise pos is ignored
            self.pos = touch.x - self.width / 2, touch.y - self.height / 2


class ShuffledWidget(BoxLayout):
    answer = StringProperty('')
    finished = BooleanProperty(False)

    gameplace = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ShuffledWidget, self).__init__(*args, **kwargs)

        for letter in self.answer:
            initial_x = random()
            initial_y = random()
            if initial_x > 0.9:
                initial_x -= 0.2
            if initial_y > 0.9:
                initial_y -= 0.2

            self.gameplace.add_widget(
                ShuffledLabel(
                    text=letter,
                    pos_hint={'x': random(), 'y': random()},
                    #pos=(random(), random()),
                    size_hint=(.1, .1)
                )
            )

    def check_answer(self, instance, value):
        self.finished = value.strip().lower() == self.answer.lower()


class Reorder(Game):
    config = ReorderConfig
    title = "Berrantolatu"
    description = "Asmatu ezkutuko hitza"
    help_txt = HELP

    def build(self):
        container = BoxLayout(orientation="vertical")

        self.shuffle_count = len(self.spec['answers'])
        self.finished_count = 0
        for answer in self.spec['answers']:
            shuffled = ShuffledWidget(answer=answer)
            shuffled.bind(finished=self.update_status)
            container.add_widget(shuffled)

        return container

    def update_status(self, instance, value):
        if value:
            self.finished_count += 1
        else:
            self.finished_count -= 1

        if self.finished_count == self.shuffle_count:
            self.exit('exit')

register_game('Reorder', Reorder, 'reorder.kv')
