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

def set_page(page: Page, page_items):
    page.total = page_items.total
    page.pageCount = (page_items.total + page_items.page_size - 1) // page_items.page_size


class PagingData(BaseModel):
    list: List[Any]
    paging: Page
