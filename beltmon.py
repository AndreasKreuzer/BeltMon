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
data_dir = "data/"

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
        parent.title("EVE Belt Monitor")

        # reading global config file
        with open(config_file) as f:
            self.config = json.load(f)

        parent.geometry(self.config["root"]["geometry"])

        # create a prompt, an input box, an output label,
        # and a button to do the computation
        self.list = tk.Listbox(parent)
        self.submit = tk.Button(parent, text="Import", command = self.importData)
        self.export = tk.Button(parent, text="Export", command = self.exportData)
        self.output = tk.Label(parent, text="")

        # lay the widgets out on the screen.
        self.list.pack(fill="both", expand=True)
        self.output.pack(side="top", fill="x", expand=True)
        self.submit.pack(side="right")
        self.export.pack(side="right")

        parent.protocol("WM_DELETE_WINDOW", self.destroyWindow)

    def destroyWindow(self):

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
        lastCol = ''
        colIndex = 1

        for line in newData:
            #TODO:
            #   - type coversions:
            #       - km in m
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

            self.list.insert("end", line)

            continue
        
        self.history.append([time.time(), newData])
        self.exportData(time.time(), newData)

        # set the output widget to have our result
        #self.output.configure(text=self.history[0])

    def exportData(self, time, obj):
        #TODO: create data dir if not exists
        with open(data_dir + str(time) + '-data.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(obj)

# if this is run as a program (versus being imported),
# create a root window and an instance of our example,
# then start the event loop

if __name__ == "__main__":
    root = tk.Tk()
    myBeltMon = BeltMon(root)
    root.mainloop()
