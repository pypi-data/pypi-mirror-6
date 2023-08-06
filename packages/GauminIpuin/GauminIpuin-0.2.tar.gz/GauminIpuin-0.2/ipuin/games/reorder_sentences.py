from . import register_game
from .base import Game, GameConfig
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.adapters.models import SelectableDataItem
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from random import shuffle

from ipuin.uix import StepSpinner


HELP = """
Esaldia berrordenatu
====================

Testua nahaste-borraste bat da!

Hautatu elemeentu bat eta eta ezkerreko botoiak erabili aurrera edo atzera mugitzeko.

Testuaren ordena egokia denean jokua bukatuko da.
"""

EDITOR_HELP = """
Esaldia berrordenatu
====================

Joku hau bi modutan jokatu daiteke, esaldi bakar batentzat edo esaldi askorentzat.

Esaldi bakar batentzat baldin bada, esaldi horretako hitzak desordenatuta agertuko dira.

Esaldi askorentzat baldin bada, esaldiak izango dira desordenatuta agertuko
direnak, esaldi barruko hitzak ordena mantenduko dutelarik.

Bi kasuetan, esaldi bakoitza lerro batean idatzi.
"""


class ReorderSentencesConfig(GameConfig):
    title = "Esaldia berrordenatu"
    description = "Ordenatu esaldi edo hitz hauek"
    help_txt = EDITOR_HELP

    def build(self):
        orientation = self.target.get('orientation', 'vertical')
        grid = GridLayout(cols=2)
        self.horizontal = CheckBox(
            group="orientation",
            active=orientation == 'horizontal',
        )
        self.vertical = CheckBox(
            group="orientation",
            active=orientation == 'vertical',
        )
        grid.add_widget(self.horizontal)
        grid.add_widget(Label(text="Esaldi bakar bat"))
        grid.add_widget(self.vertical)
        grid.add_widget(Label(text="Esaldi asko"))

        separator = (orientation == 'horizontal') and ' ' or '\n'
        sentences = separator.join(self.target.get('sentences', []))
        self.sentences = TextInput(text=sentences)
        self.exit = StepSpinner(
            key=self.target.get('exit', '---'),
            items=self.ipuin.steps,
        )

        return [
            Label(text='Mota'),
            grid,
            Label(text='Esaldiak'),
            self.sentences,
            Label(text='Helburua'),
            self.exit
        ]

    def save(self):
        if self.horizontal.active:
            self.target['orientation'] = 'horizontal'
            separator = ' '
        else:
            self.target['orientation'] = 'vertical'
            separator = '\n'
        self.target['sentences'] = self.sentences.text.split(separator)
        self.target['exit'] = self.exit.key
        self.target['target'] = 'ReorderSentences'


class HorizontalListView(ListView):
    pass


class SentenceItem(SelectableDataItem):
    def __init__(self, **kwargs):
        super(SentenceItem, self).__init__(**kwargs)
        self.text = kwargs.get('text', '')
        self.is_selected = kwargs.get('is_selected', False)


class ReorderSentencesWidget(BoxLayout):
    game = ObjectProperty()


class ReorderSentences(Game):
    config = ReorderSentencesConfig
    title = "Esaldia berrordenatu"
    help_txt = HELP

    data = ListProperty([])
    sentence_orientation = StringProperty('vertical')

    def __init__(self, spec, *args, **kwargs):
        self.sentence_orientation = spec.get('orientation', 'vertical')
        super(ReorderSentences, self).__init__(spec, *args, **kwargs)

    @property
    def description(self):
        if self.sentence_orientation == 'horizontal':
            return "Ordenatu hitz hauek"
        else:
            return "Ordenatu esaldi hauek"

    def build(self):
        container = ReorderSentencesWidget(game=self)

        shuffled_sentences = self.spec['sentences'][:]
        shuffle(shuffled_sentences)

        data = [SentenceItem(text=s) for s in shuffled_sentences]

        list_item_args_converter = \
            lambda row_index, selectable: {'text': selectable.text}

        self.sentence_adapter = \
            ListAdapter(data=data,
                        args_converter=list_item_args_converter,
                        selection_mode='single',
                        allow_empty_selection=False,
                        cls=ListItemButton)

        if self.sentence_orientation == 'horizontal':
            listView = HorizontalListView
        else:
            listView = ListView
        view = listView(
            adapter=self.sentence_adapter,
            size_hint=(0.7, 1)
        )
        container.add_widget(view)

        return container

    def move_sentence(self, direction, *args, **kwargs):
        for selected in self.sentence_adapter.selection:
            index = selected.index
            new_index = None
            if direction == "up" and index > 0:
                new_index = index - 1
            elif direction == "down" and index < len(self.sentence_adapter.data) - 1:
                new_index = index + 1
            if new_index is not None:
                value = self.sentence_adapter.data.pop(index)
                self.sentence_adapter.data.insert(new_index, value)
                self.sentence_adapter.select_list([
                    self.sentence_adapter.get_view(new_index)
                ])
                new_order = [data.text for data in self.sentence_adapter.data]
                if new_order == self.spec['sentences']:
                    self.exit('exit')


register_game('ReorderSentences', ReorderSentences, 'reorder_sentences.kv')
