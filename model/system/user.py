from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: int = Field(default=None, primary_key=True)
    user_name: str = Field(default=None, nullable=True)
    password: str = Field(default=None, nullable=True)
    salt: str = Field(default=None, nullable=True)
    email: str = Field(default=None, nullable=True, unique=True)
    gender: int = Field(default=None, nullable=True)
    nick_name: str = Field(default=None, nullable=True)
    avatar: str = Field(default=None, nullable=True)
    status: int = Field(default=None, nullable=True)
    reserve1: str = Field(default=None, nullable=True)
    reserve2: str = Field(default=None, nullable=True)
    reserve3: str = Field(default=None, nullable=True)
