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

#TODO:
#   - translations
ores = {
        'Veldspar': 1,
        'Concentrated Veldspar': 2,
        'Dense Veldspar': 3,
        'Scordite': 4,
        'Condensed Scordite': 5,
        'Massive Scordite': 6,
        'Pyroxeres': 7,
        'Solid Pyroxeres': 8,
        'Viscous Pyroxeres': 9,
        'Plagioclase': 10,
        'Azure Plagioclase': 11,
        'Rich Plagioclase': 12,
        'Omber': 13,
        'Silvery Omber': 14,
        'Golden Omber': 15,
        'Kernite': 16,
        'Luminous Kernite': 17,
        'Fiery Kernite': 18,
        'Jaspet': 19,
        'Pure Jaspet': 20,
        'Pristine Jaspet': 21,
        'Hemorphite': 22,
        'Vivid Hemorphite': 23,
        'Radiant Hemorphite': 24,
        'Hedbergite': 25,
        'Vitric Hedbergite': 26,
        'Glazed Hedbergite': 27,
        'Gneiss': 28,
        'Iridescent Gneiss': 29,
        'Prismatic Gneiss': 30,
        'Dark Ochre': 31,
        'Onyx Ochre': 32,
        'Obsidian Ochre': 33,
        'Spodumain': 34,
        'Bright Spodumain': 35,
        'Gleaming Spodumain': 36,
        'Crokite': 37,
        'Sharp Crokite': 38,
        'Crystalline Crokite': 39,
        'Bistot': 40,
        'Triclinic Bistot': 41,
        'Monoclinic Bistot': 42,
        'Arkonor': 43,
        'Crimson Arkonor': 44,
        'Prime Arkonor': 45,
        'Mercoxit': 46,
        'Magma Mercoxit': 47,
        'Vitreous Mercoxit': 48,
        'Clear Icicle': 49,
        'White Glaze': 50,
        'Blue Ice': 51,
        'Glacial Mass': 52,
        'Enriched Clear Icicle': 53,
        'Pristine White Glaze': 54,
        'Thick Blue Ice': 55,
        'Smooth Glacial Mass': 56,
        'Glare Crust': 57,
        'Dark Glitter': 58,
        'Gelidus': 59,
        'Krystallos': 60,
        }

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
            json.dump(self.config, f, indent=4)

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
            newitem['vol'] = data[3] - newdata[3]
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
                print("KeyError: for itemID of:", itemID)
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

    def importData(self):
        """Reading new scan data from clipboard."""
        result = self.master.clipboard_get()
        if (result == ""):
            self.statusMessage("No valid clipboard data")
            return

        #TODO:
        #   config for other delimiters enables import from excel?
        f = StringIO(result)
        reader = csv.reader(f, delimiter='\t')
        newData = list(reader)

        # clipboard data valid?
        try:
            if (len(newData[0]) != 4):
                self.statusMessage("No valid clipboard data")
                return
        except:
            self.statusMessage("No valid clipboard data")
            return

        # we build a new data set
        lastCol = ''
        colIndex = 1
        timestamp = time.time()
        datalist = {}
        total_types = 0
        total_asteroids = len(newData)
        total_duplicates = 0

        for line in newData:
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

            # asteroid items amount
            line[2] = int(str.replace(line[2],"'",""))

            # asteroid volume
            line[3] = str.replace(line[3],"'","")
            line[3] = int(str.replace(line[3]," m3",""))

            # distance to asteroid
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
        self.exportData(time.gmtime(timestamp), newData)

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
