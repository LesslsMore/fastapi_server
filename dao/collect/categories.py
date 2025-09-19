import logging
from typing import List, Optional

from config.data_config import CATEGORY_TREE_KEY
from dao.collect.kv_dao import KVDao
from model.collect.categories import CategoryTree


class CategoryTreeService:
    @staticmethod
    def save_category_tree(tree: CategoryTree):
        try:
            data = tree.model_dump()
            KVDao.set_value(CATEGORY_TREE_KEY, data)
        except Exception as err:
            logging.info(f"SaveCategoryTree Error: {err}")

    @staticmethod
    def get_category_tree():
        data_dict = KVDao.get_value(CATEGORY_TREE_KEY)
        # if not data:
        #     return None
        try:
            # data_dict = json.loads(data)
            tree = CategoryTree(**data_dict)
            return tree
        except Exception:
            return None

    @staticmethod
    def exists_category_tree():
        return KVDao.get_value(CATEGORY_TREE_KEY) is not None

    @classmethod
    def get_children_tree(cls, id: int) -> Optional[List[CategoryTree]]:
        tree = cls.get_category_tree()
        if not tree or not tree.children:
            return None
        for t in tree.children:
            if t.id == id:
                return t.children
        return None
