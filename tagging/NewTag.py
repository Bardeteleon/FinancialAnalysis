# from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Tag:
    definition : str
    seperator : Optional[str] = field(init=True, repr=False, default="-")
    splitted_definition : Optional[List[str]] = field(init=True, repr=False, default=None)

    def __post_init__(self):
        self.splitted_definition = self.definition.split(self.seperator)

    def __str__(self) -> str:
        return self.definition

    def __hash__(self) -> int:
        return hash(str(self))

    def contains(self, other : 'Tag') -> bool:
        if other == self:
            return True
        if len(self.splitted_definition) > len(other.splitted_definition):
            return False
        if other.splitted_definition[:len(self.splitted_definition)] == self.splitted_definition:
            return True
        else:
            return False
    
    def get_contained_tags(self) -> 'List[Tag]':
        tags : List[Tag] = []
        i = len(self.splitted_definition)
        while i > 0:
            tags.append(Tag(self.seperator.join(self.splitted_definition[:i])))
            i -= 1
        return tags


UndefinedTag = Tag("Undefined")