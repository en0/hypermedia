from os.path import dirname
from core.registrar import load_registrar

__representations__ = load_registrar(dirname(__file__), __name__, 'representations')

def next():
    for _name, _repr in __representations__.items():
        yield (_name, _repr, _repr.__resource_route__)

__all__ = [
    'next'
]

