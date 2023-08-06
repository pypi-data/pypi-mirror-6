from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.properties import ObjectProperty, StringProperty


class KeyedSpinnerOption(SpinnerOption):
    key = StringProperty(None)


class KeyedSpinner(Spinner):
    items = ObjectProperty({})
    key = StringProperty('---')

    def __init__(self, **kwargs):
        if 'option_cls' not in kwargs:
            kwargs['option_cls'] = KeyedSpinnerOption
        super(KeyedSpinner, self).__init__(**kwargs)

    def get_values(self, items):
        return items.keys()

    def item_title(self, key):
        return self.items[key].title

    def on_items(self, instance, items):
        self.values = self.get_values(items)
        self.on_key(self, self.key)

    def on_key(self, instance, key):
        if key in self.items:
            self.text = self.item_title(key)
        else:
            self.text = key

    def _update_dropdown(self, *largs):
        dp = self._dropdown
        cls = self.option_cls
        dp.clear_widgets()
        for key in self.values:
            item = cls(key=key, text=self.item_title(key))
            item.bind(on_release=lambda option: dp.select(option))
            dp.add_widget(item)

    def _on_dropdown_select(self, instance, data, *largs):
        self.key = data.key
        self.text = data.text
        self.is_open = False


class TargetTypeSpinner(KeyedSpinner):

    def get_values(self, items):
        return ['step'] + items.keys()

    def item_title(self, key):
        if key == 'step':
            return "Zuzenekoa"
        else:
            return "Jokua: %s" % self.items[key].title


class StepSpinner(KeyedSpinner):

    def item_title(self, key):
        return self.items[key].get('title', '---')
