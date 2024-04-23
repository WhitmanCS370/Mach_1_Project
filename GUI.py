import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class AudioArchiveGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Archive System")

        # File Navigation Section
        self.file_frame = ttk.Frame(root, padding="20")
        self.file_frame.grid(row=0, column=0, sticky="nsew")

        self.file_label = ttk.Label(self.file_frame, text="Select File or Upload Sound:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.upload_option = ttk.Button(self.file_frame, text="Upload Sound", command=self.upload_sound)
        self.upload_option.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.navigate_option = ttk.Button(self.file_frame, text="Navigate to Existing Sound", command=self.navigate_sound)
        self.navigate_option.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.tree = ttk.Treeview(self.file_frame, columns=("fullpath", "type"), show="tree", height=20)
        self.tree.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.tree.bind("<<TreeviewOpen>>", self.populate_tree)

        self.scrollbar = ttk.Scrollbar(self.file_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=3, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Right Section
        self.right_frame = ttk.Frame(root, padding="20")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Top Panel (Play, Pause, Stop Buttons and Dropdown)
        self.play_button = ttk.Button(self.right_frame, text="Play")
        self.play_button.grid(row=0, column=0, padx=10, pady=10)

        self.pause_button = ttk.Button(self.right_frame, text="Pause")
        self.pause_button.grid(row=0, column=1, padx=10, pady=10)

        self.stop_button = ttk.Button(self.right_frame, text="Stop")
        self.stop_button.grid(row=0, column=2, padx=10, pady=10)

        self.play_options = ttk.Combobox(self.right_frame, values=["Option 1", "Option 2", "Option 3"])
        self.play_options.grid(row=0, column=3, padx=10, pady=10)
        self.play_options.current(0)

        # Middle Panel (Editing Options)
        self.edit_frame = ttk.Frame(self.right_frame)
        self.edit_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        self.edit_options = ttk.Combobox(self.edit_frame, values=["Option 1", "Option 2", "Option 3"])
        self.edit_options.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.edit_label = ttk.Label(self.edit_frame, text="Editing Options:")
        self.edit_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.edit_button = ttk.Button(self.edit_frame, text="Apply")
        self.edit_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Bottom Panel (Audio Visualization)
        self.visualization_frame = ttk.Frame(self.right_frame)
        self.visualization_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.fig, self.ax = plt.subplots(figsize=(3, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.visualization_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

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
            file_name = os.path.basename(file_path)
            destination = os.path.join(self.folder_path, "user", file_name)
            shutil.copy(file_path, destination)
            self.populate_tree_with_folder(self.folder_path)
            print("Uploaded sound file:", file_path)
            print("Added to ESMD:", destination)

    def navigate_sound(self):
        # Populate the tree with the specified folder
        folder_path = "/Users/mollyhalverson/Desktop/Whitman/23-24/370/Mach_1_Project/Epoch123/ESMD"
        self.populate_tree_with_folder(folder_path)

def main():
    root = tk.Tk()
    app = AudioArchiveGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
