from collections.abc import Iterator
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T', bound=BaseModel)


class KalshiBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )


class ObjectList[T: BaseModel]:
    def __init__(self, items: list[T], cursor: str | None = None, has_more: bool = False):
        self._items = items
        self.cursor = cursor
        self.has_more = has_more

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __bool__(self) -> bool:
        return len(self._items) > 0

    @property
    def items(self) -> list[T]:
        return self._items

    def to_list(self) -> list[T]:
        return self._items.copy()


class KalshiResponse(KalshiBaseModel):
    success: bool = Field(default=True)
    message: str | None = Field(default=None)
    status_code: int | None = Field(default=None)
    request_id: str | None = Field(default=None)
