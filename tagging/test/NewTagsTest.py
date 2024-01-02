from typing import Dict
from tagging.NewTag import Tag
from tagging.TagGroup import TagGroup

def test_new_tag_eq():
    assert Tag("TagName") == Tag("TagName")
    assert Tag("TagName") != Tag("TagNameName")

def test_new_tag_contains():
    assert Tag("TagName-SubName").contains(Tag("TagName"))
    assert Tag("TagName").contains(Tag("TagName-SubName"))
    assert Tag("TagName").contains(Tag("TagName-SubName-SubSubName"))
    assert Tag("TagName-SubName").contains(Tag("TagName-SubName-SubSubName"))

def test_new_tag_str():
    assert str(Tag("TagName")) == "TagName"
    assert str(Tag("TagName-SubName")) == "TagName-SubName"
    assert str(Tag("TagName-SubName-SubSubName")) == "TagName-SubName-SubSubName"

def test_new_tag_as_dict_key():
    my_dict : Dict[Tag, str] = {Tag("TagName") : "MyTag"}
    assert my_dict[Tag("TagName")] == "MyTag"

def test_new_tag_get_contained_tags():
    group = TagGroup().add(Tag("TagName"))
    assert Tag("TagName").get_contained_tags() == group
    group = TagGroup().add(Tag("TagName-SubName")).add(Tag("TagName"))
    assert Tag("TagName-SubName").get_contained_tags() == group
    group = TagGroup().add(Tag("TagName-SubName-SubSubName")).add(Tag("TagName-SubName")).add(Tag("TagName"))
    assert Tag("TagName-SubName-SubSubName").get_contained_tags() == group