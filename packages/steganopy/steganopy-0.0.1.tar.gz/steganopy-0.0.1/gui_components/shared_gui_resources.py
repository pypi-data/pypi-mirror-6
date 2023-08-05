from tkFileDialog import askopenfilename
import Tkinter as Tk


class SharedGUIResources(object):

    def __init__(self, status_box):
        self.status_box = status_box

    def create_select_file_row(self, tab, label_text, entry_box_text=""):
        row = Tk.Frame(tab)
        row.pack(side=Tk.TOP, fill=Tk.X)
        file_label = Tk.Label(row, width=16, text=label_text, font=("Monospaced", 10))
        file_label.pack(side=Tk.LEFT)
        file_entry = Tk.Entry(row, width=50)
        file_entry.insert(0, entry_box_text)
        file_entry.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X)
        file_select_button = Tk.Button(row, text='Browse', command=lambda: self.select_file_dialogue(file_entry))
        file_select_button.pack(side=Tk.RIGHT, fill=Tk.X, padx=2)
        return file_entry

    def create_text_entry_row(self, tab, label_text, entry_box_text=""):
        row = Tk.Frame(tab)
        row.pack(side=Tk.TOP, fill=Tk.X)
        text_box_label = Tk.Label(row, width=16, text=label_text, font=("Monospaced", 10))
        text_box_label.pack(side=Tk.LEFT)
        text_box_entry = Tk.Entry(row, width=50)
        text_box_entry.insert(0, entry_box_text)
        text_box_entry.pack(side=Tk.LEFT, expand=Tk.NO, pady=3, fill=Tk.X)
        return text_box_entry

    def select_file_dialogue(self, entry_box):
        entry_box.delete(0, Tk.END)
        entry_box.insert(0, askopenfilename())

    def update_status_box(self, message):
        self.status_box.config(state='normal')
        self.status_box.delete(0, Tk.END)
        self.status_box.insert(0, message)
        self.status_box.config(state='readonly')
