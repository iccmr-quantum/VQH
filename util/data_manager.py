from dataclasses import dataclass, field
from time import sleep
from abc import ABC, abstractmethod
import json
from pathlib import Path

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


class FileManager(ABC):
    @abstractmethod
    def write(self, data: DataSet, filename: str) -> None:
        pass

    @abstractmethod
    def read(self, filename: str) -> DataSet:
        pass

    #def create_folder(self, folder_name: str) -> None:
    #    Path(folder_name).mkdir(parents=True, exist_ok=True)

class JSONFileHandler(FileManager):

    def read(self, filepath: str) -> list:
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data

    def write(self, dataset: DataSet, filepath: str) -> None:
        if dataset.format != 'json':
            print("Only JSON format is supported")
            raise ValueError
        #self.create_folder(Path(filepath).parent)
        with open(filepath, 'w') as file:
            json.dump(dataset.to_dict(), file)
