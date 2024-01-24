
# from __future__ import annotations Does not work together with dataconf! ...
import datetime
import dataconf
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
from data_types.Tag import Tag

@dataclass
class TagDefinition:
    tag : Tag
    comment_pattern : str
    date_from : Optional[str]
    date_to : Optional[str]

@dataclass
class TagConfig:
    tag_definitions : List[TagDefinition]

def load_tags(file_path : str) -> TagConfig:
    return dataconf.load(file_path, TagConfig)
