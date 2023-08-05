import Tkinter as Tk


class InstructionTabGUI(object):

    def create_instructions_tab(self, notebook):
        instruction_tab = Tk.Frame(notebook)
        notebook.add(instruction_tab, text="Instructions")
        self.make_text_row(instruction_tab, "")
        self.make_text_row(instruction_tab, "The encode and extract tabs provide an interface for encoding data into PNG images   ")
        self.make_text_row(instruction_tab, "and extracting data from previously created steganographic images.{0}".format(" " * 33))
        self.make_text_row(instruction_tab, "")
        self.make_text_row(instruction_tab, "You have the option of encrypting your data before it is encoded into the{0}".format(" " * 24))
        self.make_text_row(instruction_tab, "image for extra security. If you choose to encrypt the data you must use a password     ")
        self.make_text_row(instruction_tab, "that is at least eight characters in length.{0}".format(" " * 76))
        notebook.pack()

    def make_text_row(self, tab, message):
        row = Tk.Frame(tab)
        row.pack(side=Tk.TOP, fill=Tk.X)
        text_box_label = Tk.Label(row, width=73, text=message, font=("Monospaced", 10))
        text_box_label.pack(side=Tk.LEFT)
