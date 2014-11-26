import os, sys

for module in os.listdir(os.path.dirname(__file__)):
    if module != '__init__.py' and module[-3:] == '.py':
        module_name = "{0}.{1}".format(
            sys.modules[__name__].__name__,
            module[:-3]
        )
        __import__(module_name, locals(), globals())

del module

