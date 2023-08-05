import Tkinter as Tk

from os.path import sep, expanduser

from steganopy.api import create_stegano_image
from shared_gui_resources import SharedGUIResources


class EncodeTabGUI(object):

    def __init__(self, status_box):
        self.status_box = status_box
        self.resources = SharedGUIResources(self.status_box)

    def create_encode_tab(self, notebook):
            encode_tab = Tk.Frame(notebook)
            notebook.add(encode_tab, text="Encode")
            cover_file = self.resources.create_select_file_row(encode_tab, "File to hide data in*")
            data_file = self.resources.create_select_file_row(encode_tab, "           File to hide*")
            new_file_entry = self.resources.create_text_entry_row(encode_tab, "  Output file name*")
            password_entry = self.resources.create_text_entry_row(encode_tab, "Password (Optional)")
            self.encode_button_row(encode_tab, cover_file, data_file, password_entry, new_file_entry)
            notebook.pack()

    def encode_button_row(self, encode_tab, cover_file, data_file, password, new_file_entry):
            row = Tk.Frame(encode_tab)
            row.pack(side=Tk.TOP, fill=Tk.X)
            paddingL = Tk.Label(row, width=15, text='')
            paddingL.pack(side=Tk.LEFT, expand=Tk.YES)
            button = Tk.Button(
                row,
                text='Encode Data',
                command=lambda: self.encode(
                    message="Processing........",
                    cover_file=cover_file.get(),
                    data_file=data_file.get(),
                    new_file=new_file_entry.get(),
                    password=password.get()))
            button.pack(side=Tk.LEFT, pady=3, expand=Tk.YES)
            button.config(font=('Monospaced', 10, 'bold underline'))
            paddingR = Tk.Label(row, width=15, text='')
            paddingR.pack(side=Tk.LEFT, expand=Tk.YES)

    def encode(self, message, cover_file, data_file, new_file, password):
        self.resources.update_status_box(message)
        output_dir = sep.join([expanduser('~'), "Downloads"])
        try:
            image_file = create_stegano_image(original_image=cover_file, data_to_hide=data_file, cipher_key=password)
            image_file.save("{0}{1}{2}.png".format(output_dir, sep, new_file.replace(".png", "")))
            self.resources.update_status_box('{0}.pdf succssfully saved in Downloads folder'.format(new_file.replace(".png", "")))
        except Exception as e:
            self.resources.update_status_box(e)
