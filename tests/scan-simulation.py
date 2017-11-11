# import main modules
import tkinter as tk

# importing sub modules from package
from .. import *

# if this is run as a program (versus being imported),
# create a root window and an instance of our example,
# then start the event loop
if __name__ == "__main__":
    master = tk.Tk()
    myBeltMon = BeltMon(master)
    BeltMon.importFromFile('scan (5).txt')
    BeltMon.importFromFile('scan (6).txt')
    master.mainloop()
