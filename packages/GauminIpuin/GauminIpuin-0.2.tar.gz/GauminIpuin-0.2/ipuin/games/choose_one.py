from . import register_game
from .base import Game, GameConfig
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from ipuin.uix import StepSpinner

HELP = \
"""
Bat aukeratu
============

Jarraitzeko sakatu aukeratzen duzun botoia.
"""

EDITOR_HELP = \
"""
Bat aukeratu
============

Dagoen aukera bakoitzerako ipuineko zein pausura joan behar den zehaztu.
"""


class ChooseOneConfig(GameConfig):
    title = "Bat aukeratu"
    description = "Aukeratu bietako bat"
    help_txt = EDITOR_HELP

    def build(self):
        self.exit1 = StepSpinner(
            key=self.target.get('exit1', '---'),
            items=self.ipuin.steps,
        )
        self.exit2 = StepSpinner(
            key=self.target.get('exit2', '---'),
            items=self.ipuin.steps,
        )
        return [
            Label(text="Lehengo irteera"),
            self.exit1,
            Label(text="Bigarren irteera"),
            self.exit2,
        ]

    def save(self):
        self.target['exit1'] = self.exit1.key
        self.target['exit2'] = self.exit2.key
        self.target['target'] = 'ChooseOne'


class ChooseOneWidget(BoxLayout):
    pass


class ChooseOne(Game):
    exit_count = 2
    kv_file = 'choose_one.kv'
    config = ChooseOneConfig
    title = "Bat aukeratu"
    description = "Aukeratu bietako bat"
    help_txt = HELP

    def build(self):
        return ChooseOneWidget()


register_game('ChooseOne', ChooseOne)
