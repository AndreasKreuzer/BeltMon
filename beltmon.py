# import main modules
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import tkinter.ttk as ttk
from io import StringIO
import csv
import json
import time
import os
import re

# importing sub modules from package
import ui.listbox
import ui.session

# global static definitions
config_file = "conf/config.json"
data_dir = "data/"
window_title = "EVE Belt Monitor" 
columns = ['id', 'type', 'items', 'volume', 'distance']
datalist = {}

#TODO:
#   - translations
ores = {
    'Bright Spodumain': 1,
    'Crimson Arkonor': 2,
    'Iridescent Gneiss': 3,
    'Magma Mercoxit': 4,
    'Onyx Ochre': 5,
    'Sharp Crokite': 6,
    'Triclinic Bistot': 7
    }

class BeltMon:
    config = {}
    history = {}
    historylist = {}
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
        self.master = parent
        self.frame = ttk.Frame(self.master)
        self.master.title(window_title)
        
        # reading global config file
        with open(config_file) as f:
            self.config = json.load(f)

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

        # create session window
        self.sessionwindow = tk.Toplevel(self.master)
        self.sessionapp = ui.session.window(self.sessionwindow, self.config, self.historylist)

    def destroyWindow(self):
        # Only quit application if user accepts
        if (self.config["application"]["askforquit"] == 0 or
                messagebox.askokcancel(window_title, "Do you want to quit?")):
            # update config with current values
            self.config["root"]["geometry"] = self.master.geometry()

            # saving global config file
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=4)

            self.master.destroy()

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
        # reading from clipboard
        result = self.master.clipboard_get()
        if (result == ""):
            self.statusMessage("No valid clipboard data")
            return

        #TODO:
        #   config for other delimiters enables import from excel?
        f = StringIO(result)
        reader = csv.reader(f, delimiter='\t')
        newData = list(reader)

        lastCol = ''
        colIndex = 1

        # we build a new data set
        timestamp = time.time()
        datalist.clear()

        for line in newData:
            #TODO:
            #   - ensure correct data in clipboard when use of a timer
            #   - enhance
            if (len(line) != 4):
                self.statusMessage("No valid clipboard data")
                return

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

            # we build a unique id with ore type and distance
            # this is a approach to resolve a problem not a solution
            try:
                uniqueID = str(ores[line[1]]) + '_' + str(line[4])
            except:
                # ores dict not complete or no translation
                print("error building uniqueID. ore type: ", line[1])
                return

            if (uniqueID in datalist):
                # key allready exists, we have a asteroid of same type in same distance
                #   -> enhance uniqueID
                if (type(datalist[uniqueID]) == int):
                    # iterate
                    datalist[uniqueID] += 1
                    datalist[uniqueID + '_' + str(datalist[uniqueID])] = line
                else:
                    # iterate and move existing
                    datalist[uniqueID + '_1'] = datalist[uniqueID]
                    datalist[uniqueID] = 2
                    datalist[uniqueID + '_2'] = line
            else:
                # seems unique until now, insert
                datalist[uniqueID] = line
        
        # save data set in history
        self.history[timestamp] = datalist

        #TODO:
        #   - new method of treeview data into treeview
        #historylist.append([timestamp, len(newData)])
        #self.sessionapp.listbox._build_tree()

        # export data to cvs file
        #TODO:
        #   - config for bool if user wants to export automatically
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
    master = tk.Tk()
    myBeltMon = BeltMon(master)
    master.mainloop()
