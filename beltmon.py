import tkinter as tk
try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import csv
import json
import time

config_file = "conf/config.json"

class BeltMon(tk.Frame):
    config = {}
    history = []

    #TODO:
    #   - configuration of application
    #       - miner strength (m3/time)
    #       - fleet size
    #       - timer resolution
    #   - read/save configuration in JSON
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
        tk.Frame.__init__(self, parent)

        # reading global config file
        f = open(config_file)
        self.config = json.load(f)

        # create a prompt, an input box, an output label,
        # and a button to do the computation
        self.list = tk.Listbox(self)
        self.submit = tk.Button(self, text="Import", command = self.importData)
        self.export = tk.Button(self, text="Export", command = self.exportData)
        self.output = tk.Label(self, text="")

        # lay the widgets out on the screen.
        self.list.pack(fill="both", expand=True)
        self.output.pack(side="top", fill="x", expand=True)
        self.submit.pack(side="right")
        self.export.pack(side="right")

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
        #       FUCK
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
        try:
            result = self.clipboard_get()
        except:
            print("No clipboard")

        f = StringIO(result)
        reader = csv.reader(f, delimiter='\t')
        
        newData = list(reader)

        for line in newData:
            #TODO:
            #   - ids for subtypes of asteroids
            #   - type coversions:
            #       - remove m3
            #       - km in m
            #   - ensure correct data in clipboard when use of a timer

            continue
        
        self.history.append([time.time(), newData])
        self.exportData(time.time(), newData)

        
        # set the output widget to have our result
        #self.output.configure(text=self.history[0])

    def exportData(self, time, obj):
        with open(str(time) + '-data.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(obj)

# if this is run as a program (versus being imported),
# create a root window and an instance of our example,
# then start the event loop

if __name__ == "__main__":
    root = tk.Tk()
    BeltMon(root).pack(fill="both", expand=True)
    root.mainloop()
