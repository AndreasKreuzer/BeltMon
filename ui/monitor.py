# import main modules
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk

# importing sub modules from package
from . import listbox

# global static definitions
window_title = "EVE Belt Monitor" 
columns = ['index', 'type', 'distance', 'volume', 'time']

class window:
    def __init__(self, parent):
        """Constructor for monitor window class.


        Keyword arguments:
        parent -- core class

        """
        self.core = parent
        self.master = parent.monitorwindow
        self.frame = ttk.Frame(self.master)
        self.master.title(window_title)

        self.master.geometry(self.core.config["root"]["geometry"])

        # create window elements
        self.listbox = listbox.listbox(self.frame, columns)
        self.listbox.setColumns(columns)
        self.submit = ttk.Button(self.frame, text="Import", \
                command = self.core.importData)
        self.output = ttk.Label(self.frame, text="")

        # lay the widgets out on the screen.
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid(sticky='nsew')
        self.output.grid(sticky='nsw')
        self.submit.grid(sticky='e')

        self.master.protocol("WM_DELETE_WINDOW", self.destroyWindow)

    def destroyWindow(self):
        """Delete window event raised by user."""
        # Only quit application if user accepts
        if (self.core.config["application"]["askforquit"] == 0 or
                messagebox.askokcancel(window_title, "Do you want to quit?")):
            # update config with current values
            self.core.config["root"]["geometry"] = self.master.geometry()
            try:
                self.core.config["session"]["geometry"] = self.core.sessionwindow.geometry()
            except:
                # no window present
                #TODO:
                #   - this will be fixed with hide/unhide child windows instead
                #     of allowing to close and destruct by user
                print('session window allready closed by user')

            self.core.writeConfig()
            self.master.destroy()

    def configureEvent(self):
        """Read and apply configuration object from core class."""
        self.master.geometry(self.core.config["root"]["geometry"])
