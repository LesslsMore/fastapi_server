from typing import Any, List
from pydantic import BaseModel, computed_field, Field


class Page(BaseModel):
    current: int = Field(default=1, ge=0, description="当前页码")
    pageSize: int = Field(default=10, ge=1, le=500, description="每页数量")
    total: int = 0
    pageCount: int = 1

    # @computed_field
    # @property
    # def pageCount(self) -> int:
    #     return (self.total + self.pageSize - 1) // self.pageSize if self.pageSize > 0 else 0


class PagingData(BaseModel):
    list: List[Any]
    paging: Page
