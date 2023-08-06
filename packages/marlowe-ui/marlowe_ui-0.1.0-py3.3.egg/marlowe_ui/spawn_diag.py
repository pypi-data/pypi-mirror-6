import tkinter as tk
import tkinter.simpledialog

class SpawnDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent, title=None, cmdline=None, input=None, workdir=None):
        self.cmdline_raw = cmdline
        self.input = input
        self.workdir = workdir
        # Dialog.__init__ calls self.body in it 
        tkinter.simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        # comment 
        text_inst = """\
Start Marlowe Program?
Put proper command line and push "OK", or "Cancel"
(working directory: {})""".format(self.workdir)
        self.label_inst = tk.Label(master, text=text_inst, justify=tk.LEFT)
        self.label_inst.grid(row=0, column=0, sticky=tk.W)

        # command
        self.cmdline = tk.StringVar(master, self.cmdline_raw)
        self.cmdline_e = tk.Entry(master, textvariable=self.cmdline)
        self.cmdline_e.config(width=50)
        self.cmdline_e.grid(row=1, column=0, sticky=tk.W)

        # note on format
        text_notice = """NOTE: {{input}} is replaced by {}""".format(self.input)
        self.label_notice = tk.Label(master, text=text_notice, anchor=tk.E)
        self.label_notice.grid(row=2, column=0, sticky=tk.EW)

        return self.cmdline_e

    def apply(self):
        self.result = self.cmdline.get()

