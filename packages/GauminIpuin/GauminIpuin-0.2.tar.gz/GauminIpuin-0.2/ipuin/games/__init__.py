import os
from kivy.lang import Builder

registered_games = {}
registered_configs = {}


def register_game(name, klass, kv_file=None):
    registered_games[name] = klass
    registered_configs[name] = klass.get_config()
    if kv_file is not None:
        filename = os.path.join(
            os.path.dirname(__file__),
            kv_file
        )
        Builder.load_file(filename)

from . import choose_one, reorder, riddle, connect, mark_correct, reorder_sentences
