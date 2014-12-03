from importlib import import_module
from os import listdir

fns = {}

def key(label):
    def _wrapper(fn):
        fns[label] = fn
        return fn
    return _wrapper

def key_meta(label, meta):
    def _wrapper(fn):
        fns[label] = dict(fn=fn,meta=meta)
        return fn
    return _wrapper

def load_registrar(path, package, alias='fns'):
    ret = {}
    mods = set()
    for name in listdir(path):
        if name.startswith('_'): continue
        elif name[-3:] == '.py': mods.add(name[:-3])
        #elif name[-4:] == '.pyc': mods.add(name[:-4])

    for name in mods:
        mod = import_module(''.join(['.', name]), package=package)
        try:
            ret.update(getattr(mod, alias))
        except AttributeError as e:
            continue

    return ret

__all__ = [ 'key', 'fns' ]

