import tkinter as tk
from tkinter import ttk, filedialog
import os
import shutil
import wave
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

        # Editing Options Section
        self.edit_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.edit_frame, text="Editing Options")

        # Initially, display buttons for editing options
        #self.edit_metadata_button = ttk.Button(self.edit_frame, text="Edit Metadata", command=self.edit_metadata)
        #self.edit_metadata_button.grid(row=0, column=0, padx=10, pady=10)

        #self.edit_sound_button = ttk.Button(self.edit_frame, text="Edit Sound File", command=self.edit_sound)
        #self.edit_sound_button.grid(row=0, column=1, padx=10, pady=10)

        # Metadata Viewing Section
        self.metadata_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.metadata_frame, text="View Metadata")

        # Metadata Labels
        metadata_labels = ["Encoding", "Format", "Number of Channels", "Sample Rate", "File Size", "Duration"]
        self.metadata_widgets = {}
        

        for i, label in enumerate(metadata_labels):
            ttk.Label(self.metadata_frame, text=label + ":").grid(row=i, column=0, sticky="w", padx=5, pady=5)
            self.metadata_widgets[label] = ttk.Label(self.metadata_frame, text="", anchor="w")
            self.metadata_widgets[label].grid(row=i, column=1, sticky="we", padx=5, pady=5)

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
            self.display_metadata(file_path)
            self.notebook.select(2)  # Selects the third tab (index 2) where metadata is displayed


    def edit_tags(self):
        pass

    def edit_sound(self):
        pass

    def display_metadata(self, file_path):
        # Function to display metadata for a WAV file
        metadata = self.extract_wav_metadata(file_path)
        for key, value in metadata.items():
            if key in self.metadata_widgets:
                self.metadata_widgets[key].config(text=str(value))

    def extract_wav_metadata(self, file_path):
        # Function to extract metadata from a WAV file
        metadata = {}
        try:
            with wave.open(file_path, 'rb') as wav_file:
                metadata['Encoding'] = wav_file.getcomptype()
                metadata['Format'] = wav_file.getsampwidth() * 8  # Convert to bits per sample
                metadata['Number of Channels'] = wav_file.getnchannels()
                metadata['Sample Rate'] = wav_file.getframerate()
                metadata['File Size'] = os.path.getsize(file_path)
                metadata['Duration'] = wav_file.getnframes() / float(metadata['Sample Rate'])
        except Exception as e:
            print("Error:", e)
        return metadata

def main():
    root = tk.Tk()
    app = AudioArchiveGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
