import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Replace")
        self.geometry("350x200")
        self.create_widgets()

    def create_widgets(self):
        self.directory_label = tk.Label(self, text="Directory:")
        self.directory_label.grid(row=0, column=0, padx=5, pady=5)

        self.directory_entry = tk.Entry(self, width=30)
        self.directory_entry.grid(row=0, column=1, padx=5, pady=5)

        self.browse_button = tk.Button(self, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        self.find_label = tk.Label(self, text="Find:")
        self.find_label.grid(row=1, column=0, padx=5, pady=5)

        self.find_entry = tk.Entry(self, width=30)
        self.find_entry.grid(row=1, column=1, padx=5, pady=5)

        self.replace_label = tk.Label(self, text="Replace:")
        self.replace_label.grid(row=2, column=0, padx=5, pady=5)

        self.replace_entry = tk.Entry(self, width=30)
        self.replace_entry.grid(row=2, column=1, padx=5, pady=5)

        self.rename_button = tk.Button(self, text="Rename", command=self.rename_files)
        self.rename_button.grid(row=3, column=1, padx=5, pady=5)

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.directory_entry.delete(0, tk.END)
        self.directory_entry.insert(0, directory)

    def rename_files(self):
        directory = self.directory_entry.get()
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()

        if not all((directory, find_text, replace_text)):
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        text_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        total_files = len(text_files)
        self.progress['maximum'] = total_files

        for i, filename in enumerate(text_files, start=1):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                file_contents = file.read()

            new_contents = re.sub(find_text, replace_text, file_contents)

            with open(file_path, 'w') as file:
                file.write(new_contents)

            self.progress['value'] = i
            self.update_idletasks()

        messagebox.showinfo("Done", "Text replacement completed.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
