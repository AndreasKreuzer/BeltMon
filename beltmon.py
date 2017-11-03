import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import tkinter.ttk as ttk

try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import csv
import json
import time
import os
import re

# importing sub modules from package
import ui.listbox

config_file = "conf/config.json"
data_dir = "data/"
window_title = "EVE Belt Monitor" 
columns = ['id', 'type', 'items', 'volume', 'distance']
datalist = list()


class BeltMon:
    config = {}
    history = []

    #TODO:
    #   - configuration of application
    #       - miner strength (m3/time)
    #       - fleet size
    #       - timer resolution
    #   - timer for clipboard data catching
    #       - start/stop buttons
    #       - timer resolution
    #   - session handling
    #       - start a new session
    #       - session data structure (export)
    #   - show a timer for mining cycles
    #       - shows time since last scan
    #       - probably the cycles in this time
    
    def __init__(self, parent):
        self.tk = parent
        parent.title(window_title)

        # reading global config file
        with open(config_file) as f:
            self.config = json.load(f)

        parent.geometry(self.config["root"]["geometry"])

        # create window elements
        self.listbox = ui.listbox.listbox(columns, datalist)
        self.submit = tk.Button(parent, text="Import", command = self.importData)
        self.export = tk.Button(parent, text="Export", command = self.exportData)
        self.output = tk.Label(parent, text="")

        # lay the widgets out on the screen.
        #self.list.pack(fill="both", expand=True)
        self.output.pack(side="top", fill="x", expand=True)
        self.submit.pack(side="right")
        self.export.pack(side="right")

        parent.protocol("WM_DELETE_WINDOW", self.destroyWindow)

    def destroyWindow(self):
        # Only quit application if user accepts
        if (self.config["application"]["askforquit"] == 0 or
                messagebox.askokcancel(window_title, "Do you want to quit?")):
            # update config with current values
            self.config["root"]["geometry"] = self.tk.geometry()

            # saving global config file
            with open(config_file, "w") as f:
                json.dump(self.config, f)

            self.tk.destroy()

    def analyseDiff(self):
        entries = len(self.history)
        try:
            actual = self.history[entries-1]
            last = self.history[entries-2]
        except:
            return

        #TODO:
        #   - original scan (first) sets raw size
        #       -> total amount of to mined ressources
        #   - time delta
        #   - diff of volume
        #   - relative delta to time and diff of volume
        #       -> possible amount of miners
        #FEATURE:
        #   - calculate / check relative position to all asteroids
        # ------------------------
        # Save all this to:
        #   - analysedData (relative in between Scans)
        #   - progressData (over all progress)

    def showAnalysis(self):

        #TODO:
        #   - show a multi-col-view with data from analysedData
        #   - show overall progress from progressData
        
        return

    def importData(self):
        result = self.tk.clipboard_get()
        if (result == ""):
            self.statusMessage("No clipboard data")
            return

        f = StringIO(result)
        reader = csv.reader(f, delimiter='\t')
        
        newData = tuple(reader)
        lastCol = ''
        colIndex = 1

        for line in newData:
            #TODO:
            #   - ensure correct data in clipboard when use of a timer
            if (lastCol != line[0]):
                lastCol = line[0]
                colIndex = 1
            else:
                colIndex += 1

            line.insert(0, colIndex)

            line[2] = int(str.replace(line[2],"'",""))

            line[3] = str.replace(line[3],"'","")
            line[3] = int(str.replace(line[3]," m3",""))

            line[4] = str.replace(line[4],"'","")
            if (re.search(' m$', line[4])):
                line[4] =  int(str.replace(line[4], " m",""))
            else:
                line[4] =  int(str.replace(line[4], " km",""))
                line[4] = 1000 * line[4]

            datalist.insert(0, line)

            continue
        
        self.listbox._build_tree()

        self.history.append([time.time(), newData])
        self.exportData(time.time(), newData)

    def exportData(self, time, obj):
        try:
            os.stat(data_dir)
        except:
            os.mkdir(data_dir)

        with open(data_dir + str(time) + '-data.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(obj)

    def statusMessage(self, message):
        self.output.configure(text=message)

# if this is run as a program (versus being imported),
# create a root window and an instance of our example,
# then start the event loop

if __name__ == "__main__":
    root = tk.Tk()
    myBeltMon = BeltMon(root)
    root.mainloop()
