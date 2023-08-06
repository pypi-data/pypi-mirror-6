from . import register_game
from .base import Game, GameConfig
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from ipuin.uix import StepSpinner


HELP = \
"""
Asmakizuna
==========

Idatzi behekaldean asmakizunaren erantzuna. Lasai, letra larriak eta xeheak ez
dira bereizten :-)
"""

EDITOR_HELP = \
"""
Asmakizuna
==========

Asmakizunak baliozko erantzun bat baino gehiago eduki badezake, idatzi erantzun
bakoitzo lerro batean.

Letra larriak eta xeheak ez dira bereizten.
"""


class RiddleConfig(GameConfig):
    title = "Asmakizuna"
    description = "Asmakizuna"
    help_txt = EDITOR_HELP

    def build(self):
        question = self.target.get('question', '')
        self.question = TextInput(text=question)
        answers = "\n".join(self.target.get('answers', []))
        self.answers = TextInput(text=answers)
        self.exit = StepSpinner(
            key=self.target.get('exit', '---'),
            items=self.ipuin.steps,
        )

        return [
            Label(text='Galdera'),
            self.question,
            Label(text='Erantzunak'),
            self.answers,
            Label(text='Helburua'),
            self.exit
        ]

    def save(self):
        self.target['question'] = self.question.text
        self.target['answers'] = self.answers.text.split('\n')
        self.target['exit'] = self.exit.key
        self.target['target'] = 'Riddle'


class RiddleWidget(BoxLayout):
    pass


class Riddle(Game):
    question = StringProperty('')
    config = RiddleConfig
    title = "Asmakizuna"
    description = "Asmakizuna"
    help_txt = HELP

    def build(self):
        self.question = self.spec['question']
        self.answers = [x.strip().lower() for x in self.spec['answers']]
        return RiddleWidget()

    def check_answer(self, instance, value):
        if value.strip().lower() in self.answers:
            self.exit('exit')

register_game('Riddle', Riddle, 'riddle.kv')
