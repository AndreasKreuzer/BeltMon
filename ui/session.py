# import main modules
import tkinter.ttk as ttk
from tkinter import messagebox

# importing sub modules from package
from . import listbox

window_title = "Session data" 
columns = ['time', 'records']

class window:
    def __init__(self, parent, config, datalist):
        self.master = parent
        self.config = config
        self.datalist = datalist
        self.frame = ttk.Frame(self.master)
        self.master.title(window_title)
        self.master.geometry(self.config["session"]["geometry"])

        # create window elements
        self.listbox = listbox.listbox(self.frame, columns, self.datalist)
        self.button = ttk.Button(self.frame, text="foo")

        self.master.protocol("WM_DELETE_WINDOW", self.destroyWindow)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.button.grid(sticky='e')
        self.frame.grid(sticky='nsew')

    def destroyWindow(self):
        # update config with current values
        self.config["session"]["geometry"] = self.master.geometry()

        self.master.destroy()
