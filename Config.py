import dataconf
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    identifications : List[str]

def read_config(file_path : str) -> Config:
    return dataconf.load(file_path, Config)
