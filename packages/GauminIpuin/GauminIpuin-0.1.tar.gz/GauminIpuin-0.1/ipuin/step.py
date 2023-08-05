from kivy.uix.label import Label
from .uix import StepSpinner


class StepConfig(object):
    def __init__(self, ipuin, target):
        self.ipuin = ipuin
        self.target = target

    def get_widgets(self):
        height = {
            'size_hint_y': None,
            'size_y': 3,
        }
        self.widget = StepSpinner(
            key=self.target.get('target', '---'),
            items=self.ipuin.steps,
            **height
        )

        return [
            Label(
                text="Helburua",
                **height
            ),
            self.widget,
        ]

    def save(self):
        self.target['type'] = 'step'
        self.target['target'] = self.widget.key
        self.target['title'] = 'bla eta bla'
