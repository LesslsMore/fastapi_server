import logging
from urllib.parse import quote_plus

from sqlmodel import create_engine

from config.env import DataBaseConfig
from plugin.db.postgres import get_pg_config

# ASYNC_SQLALCHEMY_DATABASE_URL = (
#     f'mysql+asyncmy://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
#     f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
# )
database, host, password, port, user = get_pg_config(DataBaseConfig.POSTGRES_URL)


def set_pg_config(database, host, password, port, user):
    DataBaseConfig.db_username = user
    DataBaseConfig.db_password = password
    DataBaseConfig.db_host = host
    DataBaseConfig.db_port = port
    DataBaseConfig.db_database = database


set_pg_config(database, host, password, port, user)

# if DataBaseConfig.db_type == 'postgresql':
ASYNC_SQLALCHEMY_DATABASE_URL = (
    f'postgresql+psycopg2://{DataBaseConfig.db_username}:{quote_plus(DataBaseConfig.db_password)}@'
    f'{DataBaseConfig.db_host}:{DataBaseConfig.db_port}/{DataBaseConfig.db_database}'
)

logging.info(f"init postgres: {ASYNC_SQLALCHEMY_DATABASE_URL}")

sync_engine = create_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=DataBaseConfig.db_echo,
    max_overflow=DataBaseConfig.db_max_overflow,
    pool_size=DataBaseConfig.db_pool_size,
    pool_recycle=DataBaseConfig.db_pool_recycle,
    pool_timeout=DataBaseConfig.db_pool_timeout,
)

# async_engine = create_async_engine(
#     ASYNC_SQLALCHEMY_DATABASE_URL,
#     echo=DataBaseConfig.db_echo,
#     max_overflow=DataBaseConfig.db_max_overflow,
#     pool_size=DataBaseConfig.db_pool_size,
#     pool_recycle=DataBaseConfig.db_pool_recycle,
#     pool_timeout=DataBaseConfig.db_pool_timeout,
# )
# AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)
#
#
# class Base(AsyncAttrs, DeclarativeBase):
#     pass
