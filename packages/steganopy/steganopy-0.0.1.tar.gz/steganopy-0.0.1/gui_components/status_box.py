import Tkinter as Tk


class StatusBox(object):

    def status_box_row(self, parent):
        row = Tk.Frame(parent)
        row.pack(side=Tk.BOTTOM, fill=Tk.X)
        status_box_entry = Tk.Entry(row)
        status_box_entry.insert(0, 'Status: Ready and awaiting user input')
        status_box_entry.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X, pady=8)
        status_box_entry.config(font=('Monospaced', 10, 'bold'), state='readonly')
        return status_box_entry
