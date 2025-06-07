from typing import Any, List
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, computed_field, Field

SUCCESS = 0
FAILED = -1


class Page(BaseModel):
    current: int = Field(default=1, ge=1, description="当前页码")
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


class ResponseModel(BaseModel):
    code: int
    data: Any = None
    msg: str = ""


def result(code: int, data: Any, msg: str) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK, content=ResponseModel(code=code, data=data, msg=msg).dict())


def success(data: Any = None, message: str = "成功") -> JSONResponse:
    return result(SUCCESS, data, message)


def success_only_msg(message: str = "成功") -> JSONResponse:
    return result(SUCCESS, None, message)


def failed(message: str = "失败") -> JSONResponse:
    return result(FAILED, None, message)


def failed_with_data(data: Any, message: str = "失败") -> JSONResponse:
    return result(FAILED, data, message)


def custom_result(status_code: int, code: int, data: Any, msg: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ResponseModel(code=code, data=data, msg=msg).dict())


def exception_result(status_code: int, message: str) -> JSONResponse:
    return custom_result(status_code, SUCCESS, None, message)
