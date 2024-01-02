from typing import Dict
from tagging.NewTag import NewTag
from tagging.TagGroup import TagGroup

def test_new_tag_eq():
    assert NewTag("TagName") == NewTag("TagName")
    assert NewTag("TagName") != NewTag("TagNameName")

def test_new_tag_contains():
    assert NewTag("TagName-SubName").contains(NewTag("TagName"))
    assert NewTag("TagName").contains(NewTag("TagName-SubName"))
    assert NewTag("TagName").contains(NewTag("TagName-SubName-SubSubName"))
    assert NewTag("TagName-SubName").contains(NewTag("TagName-SubName-SubSubName"))

def test_new_tag_str():
    assert str(NewTag("TagName")) == "TagName"
    assert str(NewTag("TagName-SubName")) == "TagName-SubName"
    assert str(NewTag("TagName-SubName-SubSubName")) == "TagName-SubName-SubSubName"

def test_new_tag_as_dict_key():
    my_dict : Dict[NewTag, str] = {NewTag("TagName") : "MyTag"}
    assert my_dict[NewTag("TagName")] == "MyTag"

def test_new_tag_get_contained_tags():
    group = TagGroup().add(NewTag("TagName"))
    assert NewTag("TagName").get_contained_tags() == group
    group = TagGroup().add(NewTag("TagName-SubName")).add(NewTag("TagName"))
    assert NewTag("TagName-SubName").get_contained_tags() == group
    group = TagGroup().add(NewTag("TagName-SubName-SubSubName")).add(NewTag("TagName-SubName")).add(NewTag("TagName"))
    assert NewTag("TagName-SubName-SubSubName").get_contained_tags() == group