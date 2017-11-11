# import main modules
import tkinter as tk
from io import StringIO
import csv
import json
import time
import os
import re

# importing sub modules from package
import ui.session
import ui.monitor

# global static definitions
config_file = "conf/config.json"
data_dir = "data/"

"""
TODO:
   - configuration of application
       - miner strength (m3/time)
       - fleet size
       - timer resolution
   - timer for clipboard data catching
       - start/stop buttons
       - timer resolution
   - session handling
       - start a new session
       - session data structure (export)
   - show a timer for mining cycles
       - shows time since last scan
       - probably the cycles in this time
"""

class BeltMon:
    config = {}
    datahistory = []
    importhistory = []
    diffhistory = []
    summaryhistory = []

    monitorwindow = None
    monitor = None

    sessionwindow = None
    session = None

    def __init__(self, parent):
        """Constructor for core class.


        Keyword arguments:
        parent -- root tk object

        """
        # main tk instance
        self.master = parent

        # load global configuration
        self.loadConfig()

        # create monitor window
        self.monitorwindow = parent
        self.monitor = ui.monitor.window(self)

        # create session window
        self.sessionwindow = tk.Toplevel(self.monitorwindow)
        self.session = ui.session.window(self)

        self.configureEvent()

    def loadConfig(self):
        """Read global config file."""
        with open(config_file) as f:
            self.config = json.load(f)

    def configureEvent(self):
        """Issue configuration event on child windows."""
        self.monitor.configureEvent()
        self.monitor.configureEvent()

    def writeConfig(self):
        """Write global config file."""
        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=4, sort_keys=True)

    def analyseDiff(self):
        entries = len(self.datahistory)
        if (entries < 2):
            return
        try:
            actual = self.datahistory[entries-1]
            last = self.datahistory[entries-2]
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

        timestamp_last = last[0]
        timestamp_actual= actual[0]
        #TODO:
        #   - calculate time delta
        #   - ensure time delta is big enough (2 * minercycle)

        diffitems = {}
        diffsummary = {}
        diffsummary['vol'] = 0
        diffsummary['active'] = 0
        diffsummary['deleted'] = 0

        for itemid, data in last[1].items():
            if (type(data) == int):
                # we have a placeholder (incremental value) for duplicated ids
                continue

            newitem = {}
            newitem['states'] = []
            newitem['vol'] = 0

            try:
                newdata = actual[1][itemid]
            except:
                # id does not exist in new scan asteroid has been
                # destroyed/completly mined or user moved away
                newitem['states'].append('deleted')
                diffsummary['deleted'] += 1

                diffitems[itemid] = newitem
                continue

            if (type(newdata) == int):
                # we have a placeholder (incremental value) for duplicated ids
                continue

            # we can compare to the new scan
            newitem['vol'] = data[2] - newdata[2]
            diffsummary['vol'] += newitem['vol']

            if (newitem['vol'] > 0):
                # there is a mining occuring on that asteroid
                newitem['states'].append('active')
                diffsummary['active'] += 1
            else:
                newitem['states'].append('inactive')

            diffitems[itemid] = newitem

        self.diffhistory.append([timestamp_actual, diffitems])
        self.summaryhistory.append([timestamp_actual, diffsummary])

        self.showAnalysis()

    def showAnalysis(self):
        """Show last diff data in monitor window."""
        #TODO:
        #   - show a multi-col-view with data from analysedData
        #   - show overall progress from progressData

        self.monitor.listbox.clear()

        dataIndex = len(self.datahistory) - 1
        diffIndex = len(self.diffhistory) - 1
        for itemID, itemDiff in self.diffhistory[diffIndex][1].items():
            try:
                itemData = self.datahistory[dataIndex][1][itemID]
            except KeyError:
                if ('deleted' in itemDiff['states']):
                    itemData = self.datahistory[dataIndex - 1][1][itemID]
                else:
                    print("KeyError: for itemID of:", itemID, " state: ", itemDiff['states'])
                    continue
            values = []
            values.append(itemData[0])
            values.append(itemData[1])
            values.append(itemData[3])
            values.append(itemDiff["vol"])
            #TODO:
            #   - calculate time
            values.append("time")
            self.monitor.listbox.appendItem(itemID, itemDiff["states"], values)

        self.monitor.listbox.sortby('type',1)

    def importDataFromClipboard(self):
        """Reading new scan data from clipboard."""
        result = self.master.clipboard_get()
        if (result == ""):
            self.monitor.statusMessage("No valid clipboard data")
            return

        f = StringIO(result)
        reader = csv.reader(f, delimiter='\t')

        self.importData(list(reader))

    def importDataFromFile(self, file_path):
        """Reading new scan data from clipboard."""
        with open(file_path, "r") as f:
            reader = csv.reader(f)

            self.importData(list(reader))

    def importData(self, data):
        """Import csv data and process into application."""
        #TODO:
        #   config for other delimiters enables import from excel?
        # clipboard data valid?
        try:
            if (len(data[0]) != 4):
                self.monitor.statusMessage("No valid clipboard data")
                return
        except:
            self.monitor.statusMessage("No valid clipboard data")
            return

        # we build a new data set
        lastCol = ''
        colIndex = 1
        timestamp = time.time()
        datalist = {}
        total_types = 0
        total_asteroids = len(data)
        total_duplicates = 0

        for line in data:
            # skip if a caption label line is present
            if (len(line) != 4):
                continue

            # create asteroid type indices (only view)
            if (lastCol != line[0]):
                lastCol = line[0]
                colIndex = 1
                total_types += 1
            else:
                colIndex += 1

            line.insert(0, colIndex)

            # remove asteroid items amount
            del line[2]

            # asteroid volume
            line[2] = str.replace(line[2],"'","")
            line[2] = int(str.replace(line[2]," m3",""))

            # distance to asteroid
            line[3] = str.replace(line[3],"'","")
            if (re.search(' m$', line[3])):
                line[3] =  int(str.replace(line[3], " m",""))
            else:
                line[3] =  int(str.replace(line[3], " km",""))
                line[3] = 1000 * line[3]

            # we build a unique id with ore type and distance
            # this is a approach to resolve a problem not a solution
            try:
                uniqueID = str(self.config["ores"][line[1]]) + '_' + str(line[3])
            except:
                # ores dict not complete or no translation
                print("error building uniqueID. ore type: ", line[1])
                return

            if (uniqueID in datalist):
                # key allready exists, we have a asteroid of same type in same distance
                #   -> enhance uniqueID
                total_duplicates += 1

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
        self.datahistory.append([timestamp, datalist])

        # save and view import summary in session window
        self.importhistory.append(
                [
                    time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp)),
                    total_asteroids,
                    total_types,
                    total_duplicates
                ]
            )
        self.session.listbox.setData(self.importhistory)

        # export data to cvs file
        #TODO:
        #   - config for bool if user wants to export automatically
        self.exportData(time.gmtime(timestamp), data)

        self.analyseDiff()

    def exportData(self, timestamp, obj):
        """This writes a csv file.


        Keyword arguments:
        timestamp -- POSIX timestamp
        obj -- a list
        """
        try:
            os.stat(data_dir)
        except:
            os.mkdir(data_dir)

        with open(data_dir + time.strftime('%Y%m%d-%H%M%S', timestamp) + '.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(obj)

# if this is run as a program (versus being imported),
# create a root window and an instance of our example,
# then start the event loop
if __name__ == "__main__":
    master = tk.Tk()
    myBeltMon = BeltMon(master)
    master.mainloop()
