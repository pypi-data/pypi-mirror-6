""" extention of tk.OptionMenu which takes of pairs of (value, text)
"""

import tkinter as tk

class CodedOptionMenu(tk.OptionMenu):
    """ extention of tk.OptionMenu which takes of pairs of (value, text)
    """
    def __init__(self, master, options, **kw):
        self.cv = tk.StringVar(master)

        self.setup_optionparam(options)

        tk.OptionMenu.__init__(self, master, self.cv, *self.texts, **kw)

    def set(self, v):
        self.cv.set(self.v_to_text[v])

    def get(self):
        return self.text_to_v[self.cv.get()]

    def get_nostatechk(self):
        return self.text_to_v[self.cv.get()]

    def clear(self):
        pass

    def setup_optionparam(self, options):
        """initialize self.v_to_text, self.text_to_v, and self.texts
        """
        self.v_to_text = {}
        self.text_to_v = {}
        self.texts = []
        for v, t in options:
            self.v_to_text[v] = t
            self.text_to_v[t] = v
            self.texts.append(t)

    def set_new_option(self, options, command=None):
        """delete current options and set new options. variable does not change"""
        # delete current all menuoptions
        if len(self.texts):
            self['menu'].delete(0, len(self.texts))
        # create new textoption and translation tables
        self.setup_optionparam(options)

        # register self.text as menu, see source of Tkinter.OptionMenu.__init__
        for v in self.texts:
            self['menu'].add_command(label=v,
                    command=tk._setit(self.cv, v, command))

    def validate(self):
        return None

    def enable(self):
        self.config(state=tk.NORMAL)

    def disable(self):
        self.config(state=tk.DISABLED)

    def is_disabled(self):
        return self.cget('state') == tk.DISABLED
