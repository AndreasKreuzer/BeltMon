# import main modules
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk

# importing sub modules from package
from . import listbox

# global static definitions
window_title = "EVE Belt Monitor" 
columns = ['id', 'type', 'items', 'volume', 'distance']

class monitor:
    config = {}

    def __init__(self, parent):
        self.master = parent
        self.frame = ttk.Frame(self.master)
        self.master.title(window_title)

        self.master.geometry(self.config["root"]["geometry"])

        # create window elements
        self.listbox = ui.listbox.listbox(self.frame, columns, datalist)
        self.submit = ttk.Button(self.frame, text="Import", command = self.importData)
        self.export = ttk.Button(self.frame, text="Export", command = self.exportData)
        self.output = ttk.Label(self.frame, text="")

        # lay the widgets out on the screen.
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(sticky='nsew')
        self.output.grid(sticky='nsw')
        self.submit.grid(sticky='e')
        self.export.grid(sticky='e')

        self.master.protocol("WM_DELETE_WINDOW", self.destroyWindow)

    def destroyWindow(self):
        # Only quit application if user accepts
        if (self.config["application"]["askforquit"] == 0 or
                messagebox.askokcancel(window_title, "Do you want to quit?")):
            # update config with current values
            self.config["root"]["geometry"] = self.master.geometry()
            try:
                self.config["session"]["geometry"] = self.sessionwindow.geometry()
            except:
                # no window present
                #TODO:
                #   - this will be fixed with hide/unhide child windows instead
                #     of allowing to close and destruct by user
                print('session window allready closed by user')

            # saving global config file
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=4)

            self.master.destroy()
