import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from add_metadataGUI import TagCreationGUI

class AudioArchiveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Archive System")

        # Create a ttk Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # File Navigation Section
        self.file_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.file_frame, text="File Navigation")

        self.file_label = ttk.Label(self.file_frame, text="Select File or Upload Sound:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.upload_option = ttk.Button(self.file_frame, text="Upload Sound", command=self.upload_sound)
        self.upload_option.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.tree = ttk.Treeview(self.file_frame, columns=("fullpath", "type"), show="tree", height=20)
        self.tree.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.tree.bind("<<TreeviewOpen>>", self.populate_tree)

        self.scrollbar = ttk.Scrollbar(self.file_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=3, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Right Section
        self.right_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.right_frame, text="Editing Options")

        # Initially, display buttons for editing options
        self.edit_metadata_button = ttk.Button(self.right_frame, text="Edit Metadata", command=self.edit_metadata)
        self.edit_metadata_button.grid(row=0, column=0, padx=10, pady=10)

        self.edit_sound_button = ttk.Button(self.right_frame, text="Edit Sound File", command=self.edit_sound)
        self.edit_sound_button.grid(row=0, column=1, padx=10, pady=10)

        # Hide Right Section initially
        self.hide_right_section()

        # Populate the tree with the specified folder
        folder_path = "/Users/mollyhalverson/Desktop/Whitman/23-24/370/Mach_1_Project/Epoch123/ESMD"
        self.populate_tree_with_folder(folder_path)

    def populate_tree_with_folder(self, folder_path):
        self.tree.delete(*self.tree.get_children())
        self.populate_tree_recursively("", folder_path)

    def populate_tree_recursively(self, parent, path):
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folder_id = self.tree.insert(parent, "end", text=item, open=False, values=(full_path, "folder"))
                self.populate_tree_recursively(folder_id, full_path)
            else:
                self.tree.insert(parent, "end", text=item, open=False, values=(full_path, "file"))

    def populate_tree(self, event):
        item = self.tree.focus()
        if self.tree.item(item, "values")[1] == "drive":
            path = self.tree.item(item, "values")[0]
            self.tree.delete(self.tree.get_children(item))
            for directory in os.listdir(path):
                if os.path.isdir(os.path.join(path, directory)):
                    self.tree.insert(item, "end", text=directory, open=False, values=(os.path.join(path, directory), "folder"))
                else:
                    self.tree.insert(item, "end", text=directory, open=False, values=(os.path.join(path, directory), "file"))

    def upload_sound(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            # Open the tag creation window
            tag_window = tk.Toplevel(self.root)
            #tag_gui = TagCreationGUI(tag_window)

            # Show Right Section
            self.show_right_section()

    def edit_metadata(self):
        # Show Metadata Editing Interface
        pass

    def edit_sound(self):
        # Show Sound Editing Interface
        pass

    def show_right_section(self):
        self.notebook.select(self.right_frame)

    def hide_right_section(self):
        self.notebook.select(self.file_frame)

def main():
    root = tk.Tk()
    app = AudioArchiveGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
