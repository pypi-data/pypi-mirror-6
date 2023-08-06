from . import register_game
from .base import Game, GameConfig
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty

from ipuin.uix import StepSpinner

HELP = \
"""
Egokia hautatu
==============

Agertzen den zerrendako esaldi batzuk egiazkoak dira, beste batzuk faltsuak.

Markatu egiazko diren esaldi guztiak jokua bukatzeko.
"""

EDITOR_HELP = \
"""
Egokia hautatu
==============

**Egiazkoak** elementuan idatzi egiazkoak diren esaldiak, bat lerro bakoitzean.

**Gezurrezkoak** elementuan idatzi gezurrezkoak diren esaldiak, bat lerro bakoitzean.

Jokuak gero egiazkoak eta gezurrezkoak ausazko ordenean erakutsiko ditu
"""


class MarkCorrectConfig(GameConfig):
    title = "Egokia hautatu"
    description = "Hautatu zuzena"
    help_txt = EDITOR_HELP

    def build(self):
        true_choices = []
        false_choices = []
        for choice, is_true in self.target.get('choices', []):
            if is_true:
                true_choices.append(choice)
            else:
                false_choices.append(choice)

        self.true_choices = TextInput(text="\n".join(true_choices))
        self.false_choices = TextInput(text="\n".join(false_choices))
        self.exit = StepSpinner(
            key=self.target.get('exit', '---'),
            items=self.ipuin.steps,
        )
        return [
            Label(text='Egiazkoak'),
            self.true_choices,
            Label(text='Gezurrezkoak'),
            self.false_choices,
            Label(text='Helburua'),
            self.exit
        ]

    def save(self):
        true_choices = [[choice, True] for choice in self.true_choices.text.split("\n")]
        false_choices = [[choice, False] for choice in self.false_choices.text.split("\n")]
        self.target['choices'] = true_choices + false_choices
        self.target['exit'] = self.exit.key
        self.target['target'] = 'MarkCorrect'


class ChoiceWidget(StackLayout):
    text = StringProperty('')
    active = BooleanProperty(False)

    def update_active(self, instance, value):
        self.active = value


class MarkCorrect(Game):
    config = MarkCorrectConfig
    title = "Egokia hautatu"
    description = "Hautatu zuzena"
    help_txt = HELP

    def build(self):
        container = BoxLayout(orientation="vertical", spacing=10)

        self.answer_dict = {}
        self.choice_dict = {}

        for choice in self.spec['choices']:
            self.answer_dict[choice[0]] = choice[1]
            self.choice_dict[choice[0]] = False

            widget = ChoiceWidget(text=choice[0])
            widget.bind(active=self.update_status)
            container.add_widget(widget)

        return container

    def update_status(self, instance, value):
        self.choice_dict[instance.text] = value
        if self.choice_dict == self.answer_dict:
            self.exit('exit')


register_game('MarkCorrect', MarkCorrect, 'mark_correct.kv')
