import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk

class listbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self, parent, columns, data):
        self.master = parent
        self.columns = columns
        self.data = data
        self.tree = None
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        self.frame = ttk.Frame(self.master)
        self.frame.grid(sticky='nsew')

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show="headings")
        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.frame)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.frame)
        hsb.grid(column=0, row=1, sticky='ew', in_=self.frame)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)


    def _build_tree(self):
        for col in self.columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: self.sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))

        for item in self.data:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.columns[ix],width=None)<col_w:
                    self.tree.column(self.columns[ix], width=col_w)

    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        self.data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        self.data.sort(reverse=descending)
        for ix, item in enumerate(self.data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
            int(not descending)))


