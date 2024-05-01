import os
import json
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import yaml

class MetaData():
    def __init__(self):
        self.tags = {}
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.metadata_file_path = os.path.join(self.current_dir, "metatagdata.json")
        self.tag_file_path = os.path.join(self.current_dir, "tags.yaml")

        if not os.path.exists(self.metadata_file_path):
            with open(self.metadata_file_path, "w") as file:
                json.dump({}, file, indent=4)

        self.set_tags()

    def set_tags(self):
        with open(self.metadata_file_path, "r") as file:
            data = json.load(file)
            if not data:
                self.tags = {}
            else:
                self.tags = data

    def write_metadata(self, file_path):
        try:
            audio = AudioSegment.from_file(file_path)
        except CouldntDecodeError:
            print(f"Could not open file: {file_path}")
            return

        with open(self.metadata_file_path, "r") as file:
            data = json.load(file)
            if file_path in data:
                return
            file_name = os.path.basename(file_path)
            data[file_name] = {
                "file_path": file_path,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "duration": round(audio.duration_seconds, 2),
                "file_size": os.path.getsize(file_path),
                "sample_rate": audio.frame_rate,
                "tags": []
            }

        with open(self.metadata_file_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_file_metadata(self, file_path):
        metadata = {}
        with open(self.metadata_file_path, "r") as file:
            data = json.load(file)
            file_name = os.path.basename(file_path)
            if file_name in data:
                metadata = data[file_name]
                # print(data[file_name])

        return metadata
    
    def rename_file(self, old_path, new_path):
        with open(self.metadata_file_path, "r") as file:
            data = json.load(file)
            old_name = os.path.basename(old_path)
            new_name = os.path.basename(new_path)
            if old_name in data:
                data[new_name] = data.pop(old_name)

        with open(self.metadata_file_path, "w") as file:
            json.dump(data, file, indent=4)

    def delete_file(self, file_path):
        with open(self.metadata_file_path, "r") as file:
            data = json.load(file)
            file_name = os.path.basename(file_path)
            if file_name in data:
                data.pop(file_name)

        with open(self.metadata_file_path, "w") as file:
            json.dump(data, file, indent=4)
