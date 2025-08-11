# from __future__ import annotations
# from typing import List
# from data_types.NewTag import Tag

class TagGroup:
    def __init__(self):
        self.__tags : 'List[Tag]' = []

    def __str__(self) -> str:
        return " / ".join([str(tag) for tag in self.__tags])

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, group: 'TagGroup | str') -> bool:
        if isinstance(group, TagGroup):
            return self.__tags == group.__tags
        elif isinstance(group, str):
            return str(self) == str(group)
        else:
            return False
    
    def __iter__(self):
        return iter(self.__tags)
    
    def __next__(self):
        return next(self.__tags)

    def add(self, tag : 'Tag') -> 'TagGroup':
        self.__tags.append(tag)
        return self

    def get(self) -> 'List[Tag]':
        return self.__tags