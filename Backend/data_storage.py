import os, json
from typing import List, Type, TypeVar, Callable

T = TypeVar('T') # Meaning this variable (the data to stre) can be any type - used for nonspecific functions as this used to store all data. While Python is automatically type agnostic, I still define types where I can for code legibility

DATA_DIR = "Data"

def _get_file_path(filename: str) -> str: # Creating a /Data/ directory in the root directory of the project to store the data. If this were a full project, I'd have this connecting to a Google S3 Bucket
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return os.path.join(DATA_DIR, filename)

def save_data(objects: List[T], filename: str, to_dict_func: Callable[[T], dict]): # Data is saved in a .json file for readability
    path = _get_file_path(filename)
    with open(path, "w") as f:
        json.dump([to_dict_func(obj) for obj in objects], f, indent=4)

def load_data(filename: str, from_dict_func: Callable[[dict], T]) -> List[T]: # Fetching the data from the identified filepath
    path = _get_file_path(filename)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = json.load(f)
        return [from_dict_func(item) for item in data]
