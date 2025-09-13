from sqlmodel import Field, SQLModel

from dao.base_dao import BaseDao


class MacTypeBase(SQLModel):
    type_name: str = Field(default='', max_length=60, nullable=False)
    type_en: str = Field(default='', max_length=60, nullable=False)
    type_sort: int = Field(default=0, ge=0, le=65535, nullable=False)  # smallint unsigned
    type_mid: int = Field(default=1, ge=0, le=65535, nullable=False)  # smallint unsigned
    type_pid: int = Field(default=0, ge=0, le=65535, nullable=False)  # smallint unsigned
    type_status: int = Field(default=1, ge=0, le=255, nullable=False)  # tinyint unsigned
    type_tpl: str = Field(default='', max_length=30, nullable=False)
    type_tpl_list: str = Field(default='', max_length=30, nullable=False)
    type_tpl_detail: str = Field(default='', max_length=30, nullable=False)
    type_tpl_play: str = Field(default='', max_length=30, nullable=False)
    type_tpl_down: str = Field(default='', max_length=30, nullable=False)
    type_key: str = Field(default='', max_length=255, nullable=False)
    type_des: str = Field(default='', max_length=255, nullable=False)
    type_title: str = Field(default='', max_length=255, nullable=False)
    type_union: str = Field(default='', max_length=255, nullable=False)
    type_extend: str = Field(default='', nullable=False)  # text 类型
    type_logo: str = Field(default='', max_length=255, nullable=False)
    type_pic: str = Field(default='', max_length=1024, nullable=False)
    type_jumpurl: str = Field(default='', max_length=150, nullable=False)


class MacType(MacTypeBase, table=True):
    __tablename__ = "mac_type"
    type_id: int = Field(default=None, primary_key=True, nullable=True)  # smallint unsigned + auto-increment


mac_type_dao = BaseDao(MacType)
