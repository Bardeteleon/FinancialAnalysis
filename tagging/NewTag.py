from __future__ import annotations
from typing import List
from tagging.TagGroup import TagGroup

class NewTag:
    def __init__(self, definition : str):
        self.__seperator : str = "-"
        self.__definition : List[str] = definition.split(self.__seperator)

    def __eq__(self, other: NewTag) -> bool:
        if other.__definition == self.__definition:
            return True
    
    def __str__(self) -> str:
        return self.__seperator.join(self.__definition)
    
    def __hash__(self) -> int:
        return hash(str(self))

    def contains(self, other : NewTag) -> bool:
        if other == self:
            return True
        min_len = min(len(other.__definition), len(self.__definition))
        if other.__definition[:min_len] == self.__definition[:min_len]:
            return True
        else:
            return False
    
    def get_contained_tags(self) -> TagGroup:
        group = TagGroup()
        i = len(self.__definition)
        while i > 0:
            group.add(NewTag(self.__seperator.join(self.__definition[:i])))
            i -= 1
        return group