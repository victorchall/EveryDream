# Python GUI tool to manually caption images for machine learning.
# A sidecar file is created for each image with the same name and a .txt extension.
#
# [control/command + o] to open a folder of images.
# [page down] and [page up] to go to next and previous images. Hold shift to skip 10 images.
# [shift + home] and [shift + end] to go to first and last images.
# [shift + delete] to move the current image into a '_deleted' folder.
# [escape] to exit the app.

import os
import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pathlib import Path

class ImageView(tk.Frame):

    filename = None
    caption = None

    folder = None
    image_path = None
    image_list = []
    image_index = 0
    image_widget = None
    filename_widget = None
    caption_field = None

    def __init__(self, root):
        tk.Frame.__init__(self, root)

        # create a 2x2 grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # filename
        self.filename = tk.StringVar()
        self.filename_widget = tk.Label(self, textvariable=self.filename)
        self.filename_widget.grid(row=0, column=0, columnspan=2, sticky=tk.N + tk.W + tk.E)
        # image
        self.image_widget = tk.Label(self)
        self.image_widget.grid(row=1, column=0, sticky=tk.W + tk.S + tk.N)
        # caption field
        self.caption_field = tk.Text(self, wrap="word")
        self.caption_field.grid(row=1, column=1, sticky=tk.E + tk.S + tk.N)

    def open_folder(self):
        self.folder = Path(filedialog.askdirectory())
        if self.folder is None:
            return
        self.image_list.clear()
        for file in os.listdir(self.folder):
            f = Path(file)
            if f.suffix == '.jpg' or f.suffix == '.png':
                self.image_list.append(f)
        self.image_list.sort()
        self.load_image()
        self.load_label_txt()
    
    def load_image(self):
        self.image_path = self.folder / self.image_list[self.image_index]
        self.filename.set(self.image_list[self.image_index])
        img = Image.open(self.image_path)
        if img.width > root.winfo_width() or img.height > root.winfo_height():
            img.thumbnail((800, 800))
        img = ImageTk.PhotoImage(img)
        self.image_widget.configure(image=img)
        self.image_widget.image = img
    
    def write_label_txt(self):
        label_txt_file = self.folder / (self.image_list[self.image_index].stem + '.txt')
        # overwrite label text file with the current text
        current_label_text = self.caption_field.get("1.0", "end-1c")
        current_label_text = current_label_text.replace('\r', '').replace('\n', '').strip()
        if current_label_text != '':
            print('wrote label text to file: ' + str(label_txt_file))
            with open(str(label_txt_file.absolute()), 'w') as f:
                f.write(current_label_text)
        
    def load_label_txt(self):
        # load label text file for the new image
        self.caption_field.delete(1.0, tk.END)
        label_txt_file = self.folder / (self.image_list[self.image_index].stem + '.txt')
        if label_txt_file.exists():
            with open(str(label_txt_file.absolute()), 'r') as f:
                self.caption_field.insert(tk.END, f.read())

    def go_to_image(self, index):
        self.write_label_txt()
        self.image_index = index
        self.load_label_txt()
        self.load_image()

    def next_image(self):
        self.write_label_txt()
        self.image_index += 1
        if self.image_index >= len(self.image_list):
            self.image_index = 0
        self.load_label_txt()
        self.load_image()

    def prev_image(self):
        self.write_label_txt()
        self.image_index -= 1
        if self.image_index < 0:
            self.image_index = len(self.image_list) - 1
        self.load_label_txt()
        self.load_image()

    # move current image to a "_deleted" folder
    def delete_image(self):
        if len(self.image_list) == 0:
            return
        cur_image_name = self.image_list[self.image_index]
        cur_image_path = self.folder / cur_image_name
        self.next_image()
        deleted_folder = Path(self.folder / '_deleted')
        if not deleted_folder.exists():
            deleted_folder.mkdir()
        os.rename(cur_image_path, deleted_folder / cur_image_name)
        # move the corresponding text file to the deleted folder
        txt_file_name = cur_image_name.stem + '.txt'
        label_txt_file = self.folder / txt_file_name
        if label_txt_file.exists():
            os.rename(label_txt_file, deleted_folder / txt_file_name)
    
if __name__=='__main__':
    root = tk.Tk()
    root.geometry('1200x800')
    root.title('Image Captions')

    if sys.platform == 'darwin':
        root.bind('<Command-o>', lambda e: view.open_folder())
    else:
        root.bind('<Control-o>', lambda e: view.open_folder())
    root.bind('<Escape>', lambda e: root.destroy())
    root.bind('<Prior>', lambda e: view.prev_image())
    root.bind('<Next>', lambda e: view.next_image())
    root.bind('<Shift-Prior>', lambda e: view.go_to_image(view.image_index - 10))
    root.bind('<Shift-Next>', lambda e: view.go_to_image(view.image_index + 10))
    root.bind('<Shift-Home>', lambda e: view.go_to_image(0))
    root.bind('<Shift-End>', lambda e: view.go_to_image(len(view.image_list) - 1))
    root.bind('<Shift-Delete>', lambda e: view.delete_image())

    view = ImageView(root)
    view.pack(side="top", fill="both", expand=True)
    root.mainloop()