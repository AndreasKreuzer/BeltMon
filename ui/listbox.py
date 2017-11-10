import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk

class listbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self, parent, columns):
        """Init treeview class."""
        self.master = parent
        self.columns = columns
        self.data = []
        self.tree = None
        self._setup_widgets()

    def _setup_widgets(self):
        """This setups the window widgets."""
        self.frame = ttk.Frame(self.master)
        self.frame.grid(sticky='nsew')

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(self.frame, columns=self.columns, \
                show="headings")
        vsb = ttk.Scrollbar(self.frame, orient="vertical", \
                command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame, orient="horizontal", \
                command=self.tree.xview)

        # configure layout with treeview grid method.
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.frame)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.frame)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.frame)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

    def _build_headers(self):
        """Setup treeview column headers."""
        for col in self.columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: self._sortby(c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

    def _build_by_data(self):
        """This build treeview by given data."""
        for item in self.data:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.columns[ix],width=None)<col_w:
                    self.tree.column(self.columns[ix], width=col_w)

    def _sortby(self, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        self.data = [(self.tree.set(child, col), child) \
            for child in self.tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        self.data.sort(reverse=descending)
        for ix, item in enumerate(self.data):
            self.tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        self.tree.heading(col, command=lambda col=col: self._sortby(col, \
            int(not descending)))

    def setColumns(self, columns):
        """Set columns and update treeview."""
        self.columns = columns
        self._build_headers()

    def setData(self, data):
        """Set data and reset/populate data to treeview."""
        self.clear()
        self.data = data
        self._build_by_data()

    def clear(self):
        """Reset data and treeview."""
        self.data = []
        for item in self.tree.get_children():
            self.tree.delete(item)

    def appendItem(self, itemID, itemTags, values):
        """Append a item to treeview data and show it."""
        #TODO:
        #   - sorted insert
        newid = self.tree.insert('', 'end', values=values, tags=itemTags, iid=itemID)
        newvalues = values
        newvalues.append(newid)
        self.data.append(values)

    def updateItem(self, itemID, itemTags, values):
        """Update tags annd values of an item and populate to treeview."""
        #TODO:
        #   - sorted update
        self.tree.item(itemID, tags=itemTags, values=values)
