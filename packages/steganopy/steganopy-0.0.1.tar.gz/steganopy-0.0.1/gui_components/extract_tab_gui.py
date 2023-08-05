import Tkinter as Tk

from os.path import sep, expanduser

from steganopy.api import extract_data_from_stegano_image
from shared_gui_resources import SharedGUIResources


class ExtractTabGUI(object):

    def __init__(self, status_box):
        self.status_box = status_box
        self.resources = SharedGUIResources(self.status_box)

    def create_extract_tab(self, notebook):
        extract_tab = Tk.Frame(notebook)
        notebook.add(extract_tab, text="Extract")
        image_with_data = self.resources.create_select_file_row(extract_tab, "        File with data*")
        new_file_entry = self.resources.create_text_entry_row(extract_tab, "  Save contents as*")
        password_entry = self.resources.create_text_entry_row(extract_tab, "Password (Optional)")
        self.extract_button_row(extract_tab, image_with_data, password_entry, new_file_entry)
        notebook.pack()

    def extract_button_row(self, extract_tab, image_with_data, password, new_file_entry):
            row = Tk.Frame(extract_tab)
            row.pack(side=Tk.TOP, fill=Tk.X)
            paddingL = Tk.Label(row, width=15, text='')
            paddingL.pack(side=Tk.LEFT, expand=Tk.YES)
            button = Tk.Button(
                row,
                text='Extract Data',
                command=lambda: self.extract(
                    message="Processing........",
                    image_with_data=image_with_data.get(),
                    new_file=new_file_entry.get(),
                    password=password.get()))
            button.pack(side=Tk.LEFT, pady=3, expand=Tk.YES)
            button.config(font=('Monospaced', 10, 'bold underline'))
            paddingR = Tk.Label(row, width=15, text='')
            paddingR.pack(side=Tk.LEFT, expand=Tk.YES)

    def extract(self, message, image_with_data, new_file, password):
        self.resources.update_status_box(message)
        output_dir = sep.join([expanduser('~'), "Downloads"])
        try:
            extracted_content = extract_data_from_stegano_image(image=image_with_data, cipher_key=password)
            self.write_extracted_content_to_file(extracted_content, "{0}{1}{2}".format(output_dir, sep, new_file))
            self.resources.update_status_box('Extraction successful {0} saved in Downloads folder'.format(new_file))
        except Exception as e:
            self.resources.update_status_box(e)

    def write_extracted_content_to_file(self, content_to_write, save_as):
        with open(save_as, "w") as f:
            f.write(content_to_write)
