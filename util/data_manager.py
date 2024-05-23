from dataclasses import dataclass, field
from time import sleep
from abc import ABC, abstractmethod
from typing import Protocol
import json
import os
import re

@dataclass
class DataSet:
    data: list = field(default_factory=list)
    format: str = "json"  # Default format

    def to_dict(self):
        raise NotImplementedError
        #return self.data

    def plot(self):
        if self.format == 'json':
            # Example processing for plotting from a dictionary
            pass
        print("RT Data plotter not implemented yet")
        sleep(2)
        raise NotImplementedError

    def append_data(self, data: dict) -> None:
        self.data.append(data)

    def cleanup(self) -> None:
        self.data = []

    def __iadd__(self, data: dict):
        self.append_data(data)
        return self

class FileIO(Protocol):
    def read(self, filepath: str) -> DataSet:
        ...

    def write(self, dataset: DataSet, filepath: str) -> None:
        ...

class JSONFileIO:
    def __init__(self):
        self.format = 'json'

    def read(self, filepath: str) -> DataSet:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return DataSet(data=data)

    def write(self, dataset: DataSet, filepath: str) -> None:
        with open(filepath, 'w') as file:
            json.dump(dataset.to_dict(), file)

FORMATS = {
        "json": JSONFileIO
}


class VQHDataFileManager:
    def __init__(self, folder_name: str):
        self.folder_name = folder_name
        self.create_parent_folder(self.folder_name)
        self.latest_index = self.get_latest_index(self.folder_name)
        self.file_io: FileIO = JSONFileIO() # Default
        print(f"Latest index: {self.latest_index}")

    def write(self, data: DataSet, filename: str) -> None:
        raise NotImplementedError

    def read(self, index: int = None) -> DataSet:
        if not index:
            index = self.latest_index

        pattern = re.compile(r'son_data\.(.*)')
        try:
            files = os.listdir(f'{self.folder_name}/Data_{index}')
        except FileNotFoundError:
            print(f"Experiment folder not found for index {index}. Going to default folder")
            raise NotImplementedError


        data_files = [file for file in files if pattern.match(file)]
        if len(data_files) == 0:
            print(f"No data files found for index {index}")
            raise FileNotFound
        elif len(data_files) > 1:
            print(f"Multiple data files found for index {index}. Using the first one")

        data_file = data_files[0]
        extension = pattern.match(data_file).group(1)

        if self.file_io.format != extension:
            try:
                self.file_io = FORMATS.get(extension)()
            except KeyError:
                print(f"File extension {extension} not supported")
                raise NotImplementedError
        

        return self.file_io.read(f'{self.folder_name}/Data_{index}/{data_file}')



    def create_parent_folder(self, folder_name: str) -> None:
        print(f"Creating folder: {folder_name}")
        os.makedirs(folder_name, exist_ok=True)

    def get_latest_index(self, folder_name: str) -> int:
        files = os.listdir(folder_name)
        pattern = re.compile(r'Data_(\d+)')
        data_indexes = [int(pattern.match(file).group(1)) for file in files if pattern.match(file)]
        if len(data_indexes) == 0:
            return 0
        else:
            return max(data_indexes)


