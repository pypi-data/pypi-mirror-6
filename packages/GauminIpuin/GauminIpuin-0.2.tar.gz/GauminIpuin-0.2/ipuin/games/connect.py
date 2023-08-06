import random
from . import register_game
from .base import Game, GameConfig
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics import Color, Line

from ipuin.uix import StepSpinner

HELP = \
"""
Konektatu
=========

Ezkerraldean dauden elementu bakoitza eskuinaldeko elementu batekin lotu.

Sakatu ezkerreko elementu batean eta arrastatu dagokion eskuineko elementura
elkarren artean lotzeko marra agertu dadin. Marra guztiak ongi daudenean jokua
bukatuko duzu.
"""

EDITOR_HELP = \
"""
Konektatu
=========

Idatzi lerro bakoitzean ezkerrean joango den elementua, koma, eta eskuinean joango dena.

Adib::

    txakurra,katua
    bat,bi
"""


class ConnectConfig(GameConfig):
    title = "Konektatu"
    description = "Lotu erlazionatutakoak"
    help_txt = EDITOR_HELP

    def build(self):
        text = "\n".join(["%s,%s" % (key, value) for key, value in self.target.get('items', {}).items()])
        self.items = TextInput(text=text)
        self.exit = StepSpinner(
            key=self.target.get('exit', '---'),
            items=self.ipuin.steps,
        )
        return [
            Label(text='Elementuak'),
            self.items,
            Label(text='Helburua'),
            self.exit
        ]

    def save(self):
        text = self.items.text
        items = dict([a.split(',') for a in text.split("\n")])
        self.target['items'] = items
        self.target['exit'] = self.exit.key
        self.target['target'] = 'Connect'


class KeyLabel(AnchorLayout):
    text = StringProperty('')
    label = ObjectProperty(None)
    line = ObjectProperty(None)
    pointer = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            if self.line is None:
                with self.canvas.before:
                    Color(0, 0, 1)
                    self.line = Line(points=[self.center_x, self.center_y,
                                             self.center_x + self.label.width, self.center_y])
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.pointer = touch.pos
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.line.points.pop()
            self.line.points.pop()
            self.line.points += [touch.x, touch.y]


class ValueLabel(AnchorLayout):
    text = StringProperty('')


class Connect(Game):
    config = ConnectConfig
    title = "Konektatu"
    description = "Lotu erlazionatutakoak"
    help_txt = HELP

    def build(self):
        widget = GridLayout(cols=2)

        keys = self.spec['items'].keys()
        values = self.spec['items'].values()
        random.shuffle(values)

        self.value_widgets = []
        self.solved = set()

        for key, value in zip(keys, values):
            label = KeyLabel(text=key)
            label.bind(pointer=self.check_connection)
            widget.add_widget(label)
            label = ValueLabel(text=value)
            widget.add_widget(label)
            self.value_widgets.append(label)

        return widget

    def check_connection(self, instance, position):
        for widget in self.value_widgets:
            if widget.collide_point(*position):
                if self.spec['items'][instance.text] == widget.text:
                    self.solved.add(instance.text)
                else:
                    self.solved.difference_update([instance.text])
                break
        if len(self.solved) == len(self.spec['items']):
            self.exit('exit')


register_game('Connect', Connect, 'connect.kv')
