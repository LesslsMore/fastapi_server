import logging
from typing import List, Optional

from config.data_config import CATEGORY_TREE_KEY
from dao.collect.kv_dao import KVDao
from model.collect.MacType import MacType, mac_type_dao
from model.collect.category import CategoryTree


class CategoryService:
    @staticmethod
    def get_category_tree_by_db():
        mac_type_list: List[MacType] = mac_type_dao.query_items({'type_status': 1})
        cl = [mac_type.model_dump() for mac_type in mac_type_list]
        category_tree = CategoryService.gen_category_tree(cl)

        CategoryService.save_category_tree(category_tree)

    @staticmethod
    def gen_category_tree(film_classes):
        tree = CategoryTree(id=0, pid=-1, name="分类信息", show=True)
        temp = {tree.id: tree}

        for c in film_classes:
            category = temp.get(c['type_id'])
            if category:
                category.id = c['type_id']
                category.pid = c['type_pid']
                category.name = c['type_name']
                category.show = True
            else:
                category = CategoryTree(id=c['type_id'], pid=c['type_pid'], name=c['type_name'], show=True)
                temp[c['type_id']] = category

            parent = temp.get(category.pid)
            if not parent:
                parent = CategoryTree(id=c['type_pid'], pid=0, name="", show=True)
                temp[c['type_pid']] = parent

            parent.children.append(category)

        return tree

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
