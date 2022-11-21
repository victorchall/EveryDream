# Python GUI tool to manually caption images for machine learning.
# A sidecar file is created for each image with the same name and a .txt extension.
#
# [control/command + o] to open a folder of images.
# [page down] and [page up] to go to next and previous images. Hold shift to skip 10 images.
# [shift + home] and [shift + end] to go to first and last images.
# [shift + delete] to move the current image into a '_deleted' folder.
# [escape] to exit the app.

import sys
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from pathlib import Path

class CaptionedImage():
    def __init__(self, image_path):
        self.base_path = image_path.parent
        self.path = image_path
    
    def caption_path(self):
        return self.base_path / (self.path.stem + '.txt')

    def read_caption(self):
        caption_path = self.caption_path()
        if caption_path.exists():
            with open(caption_path, 'r', encoding='utf-8', newline='') as f:
                return f.read()
        return ''

    def write_caption(self, caption):
        caption_path = self.caption_path()
        with open(str(caption_path), 'w', encoding='utf-8', newline='') as f:
            f.write(caption)
    
    # sort
    def __lt__(self, other):
        return self.path < other.path

class ImageView(tk.Frame):

    def __init__(self, root):
        tk.Frame.__init__(self, root)

        self.base_path = None
        self.images = []
        self.index = 0

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
        self.base_path = Path(filedialog.askdirectory())
        if self.base_path is None:
            return
        self.images.clear()
        for file in self.base_path.glob('*.[jp][pn][gg]'): # jpg or png
            self.images.append(CaptionedImage(file))
        self.images.sort()
        self.update_ui()
    
    def store_caption(self):
        txt = self.caption_field.get(1.0, tk.END)
        txt = txt.replace('\r', '').replace('\n', '').strip()
        self.images[self.index].write_caption(txt)
        
    def set_index(self, index):
        self.index = index % len(self.images)

    def go_to_image(self, index):
        if len(self.images) == 0:
            return
        self.store_caption()
        self.set_index(index)
        self.update_ui()

    def next_image(self):
        self.go_to_image(self.index + 1)

    def prev_image(self):
        self.go_to_image(self.index - 1)

    # move current image to a "_deleted" folder
    def delete_image(self):
        if len(self.images) == 0:
            return
        img = self.images[self.index]

        trash_path = self.base_path / '_deleted'
        if not trash_path.exists():
            trash_path.mkdir()
        img.path.rename(trash_path / img.path.name)
        caption_path = img.caption_path()
        if caption_path.exists():
            caption_path.rename(trash_path / caption_path.name)

        del self.images[self.index]
        self.update_ui()
    
    def update_ui(self):
        if (len(self.images)) == 0:
            self.filename.set('')
            self.caption_field.delete(1.0, tk.END)
            self.image_widget.configure(image=None)
            return
        img = self.images[self.index]
        # filename
        self.filename.set(self.images[self.index].path.name)
        # caption
        self.caption_field.delete(1.0, tk.END)
        self.caption_field.insert(tk.END, img.read_caption())
        # image
        img = Image.open(self.images[self.index].path)
        img = ImageTk.PhotoImage(img)
        self.image_widget.configure(image=img)
        self.image_widget.image = img
    
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
    root.bind('<Shift-Prior>', lambda e: view.go_to_image(view.index - 10))
    root.bind('<Shift-Next>', lambda e: view.go_to_image(view.index + 10))
    root.bind('<Shift-Home>', lambda e: view.go_to_image(0))
    root.bind('<Shift-End>', lambda e: view.go_to_image(len(view.images) - 1))
    root.bind('<Shift-Delete>', lambda e: view.delete_image())

    view = ImageView(root)
    view.pack(side="top", fill="both", expand=True)
    root.mainloop()