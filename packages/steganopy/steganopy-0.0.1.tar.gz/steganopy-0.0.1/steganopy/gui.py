#!/usr/bin/python
import ttk
import Tkinter as Tk

from gui_components.encode_tab_gui import EncodeTabGUI
from gui_components.extract_tab_gui import ExtractTabGUI
from gui_components.instructions_tab_gui import InstructionTabGUI
from gui_components.status_box import StatusBox


class GUI(Tk.Frame):

    def __init__(self, parent=None):
        Tk.Frame.__init__(self, parent)
        self.pack(expand=Tk.YES, fill=Tk.BOTH)
        notebook = ttk.Notebook(parent)
        self.status_box = StatusBox().status_box_row(parent)
        EncodeTabGUI(self.status_box).create_encode_tab(notebook)
        ExtractTabGUI(self.status_box).create_extract_tab(notebook)
        InstructionTabGUI().create_instructions_tab(notebook)


def main():
    root = Tk.Tk()
    root.title('Steganopy')
    GUI(root).mainloop()
    root.destroy()
