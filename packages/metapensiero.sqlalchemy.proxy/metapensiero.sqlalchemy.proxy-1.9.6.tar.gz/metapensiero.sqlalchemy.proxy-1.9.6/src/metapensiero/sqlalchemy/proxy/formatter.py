# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy -- Output formatter base class and registry
# :Creato:    sab 29 mag 2010 17:41:50 CEST
# :Autore:    Alberto Berti <azazel@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

class BaseFormatter(object):
    "I'm used to format the output to a given format. See .pylons module for the usage."
    _registry = {}

    @classmethod
    def register(class_, *formats):
        for f in formats:
            class_._registry[f] = class_

    @classmethod
    def bind(class_, format):
        return class_._registry[format]

    def __init__(self, *args, **kw):
        self.func = args[0]
        self.args = args[1:]
        self.kw = kw

    def __call__(self, session):
        "The session is an sqlalchemy's one"
        return self.func(session, *self.args, **self.kw)
