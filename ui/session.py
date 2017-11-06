# import main modules
import tkinter.ttk as ttk
from tkinter import messagebox

# importing sub modules from package
from . import listbox

window_title = "Session data" 
columns = ['time', 'total asteroids', 'asteroid types', 'asteroid overlaps']

class window:
    def __init__(self, parent):
        """Constructor for monitor window class.


        Keyword arguments:
        parent -- core class

        """
        self.core = parent
        self.master = parent.sessionwindow
        self.frame = ttk.Frame(self.master)
        self.master.title(window_title)
        self.master.geometry(self.core.config["session"]["geometry"])

        # create window elements
        self.listbox = listbox.listbox(self.frame, columns)
        self.listbox.setColumns(columns)
        self.button = ttk.Button(self.frame, text="foo")

        self.master.protocol("WM_DELETE_WINDOW", self.destroyWindow)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.button.grid(sticky='e')
        self.frame.grid(sticky='nsew')

    def destroyWindow(self):
        """Window delete event raised by user."""
        self.core.config["session"]["geometry"] = self.master.geometry()

        #TODO:
        #   - hide/show window instead of delete tk object."
        self.master.destroy()

    def configureEvent(self):
        """Read and apply configuration object from core class."""
        self.master.geometry(self.core.config["session"]["geometry"])
