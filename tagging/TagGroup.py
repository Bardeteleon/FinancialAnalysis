# from __future__ import annotations
# from typing import List
# from tagging.NewTag import Tag

class TagGroup:
    def __init__(self):
        self.__tags : 'List[Tag]' = []

    def __str__(self) -> str:
        return " / ".join(self.__tags)

    def __hash__(self) -> int:
        return str(hash(self))

    def __eq__(self, group: 'TagGroup') -> bool:
        return self.__tags == group.__tags

    def add(self, tag : 'Tag') -> 'TagGroup':
        self.__tags.append(tag)
        return self