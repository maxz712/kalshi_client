from pydantic import BaseModel

from kalshi_client.models.base import ObjectList


class MockObject(BaseModel):
    id: str
    name: str


class TestObjectList:
    def test_initialization(self):
        items = [MockObject(id="1", name="Item 1"), MockObject(id="2", name="Item 2")]
        obj_list = ObjectList(items=items, cursor="cursor123", has_more=True)

        assert len(obj_list) == 2
        assert obj_list.cursor == "cursor123"
        assert obj_list.has_more is True

    def test_iteration(self):
        items = [MockObject(id="1", name="Item 1"), MockObject(id="2", name="Item 2")]
        obj_list = ObjectList(items=items)

        names = [item.name for item in obj_list]
        assert names == ["Item 1", "Item 2"]

    def test_indexing(self):
        items = [MockObject(id="1", name="Item 1"), MockObject(id="2", name="Item 2")]
        obj_list = ObjectList(items=items)

        assert obj_list[0].id == "1"
        assert obj_list[1].name == "Item 2"

    def test_boolean_conversion(self):
        empty_list = ObjectList(items=[])
        assert bool(empty_list) is False

        non_empty_list = ObjectList(items=[MockObject(id="1", name="Item 1")])
        assert bool(non_empty_list) is True

    def test_to_list(self):
        items = [MockObject(id="1", name="Item 1"), MockObject(id="2", name="Item 2")]
        obj_list = ObjectList(items=items)

        result = obj_list.to_list()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].id == "1"
        assert result is not items  # Should be a copy

    def test_items_property(self):
        items = [MockObject(id="1", name="Item 1")]
        obj_list = ObjectList(items=items)

        assert obj_list.items == items
        assert obj_list.items is items  # Should be the same reference

    def test_default_values(self):
        items = [MockObject(id="1", name="Item 1")]
        obj_list = ObjectList(items=items)

        assert obj_list.cursor is None
        assert obj_list.has_more is False
