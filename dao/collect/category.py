from typing import List, Optional, Dict, Any

from pydantic import TypeAdapter

from model.collect.MacType import MacType, mac_type_dao
from model.collect.category import CategoryTree


class CategoryService:
    @staticmethod
    def get_nav_category(tree) -> List[Dict[str, Any]]:
        cate_list = []
        for child in tree.children:
            if child.show:
                cate_list.append(child)
        return cate_list

    @staticmethod
    def get_category_tree_by_db(filter_dict: dict = {'type_status': 1}):
        mac_type_list: List[MacType] = mac_type_dao.query_items(filter_dict)
        cl = [mac_type.model_dump() for mac_type in mac_type_list]
        category_tree = CategoryService.gen_category_tree(cl)
        return category_tree

    @staticmethod
    def get_category_tree():
        mac_type_list: List[MacType] = mac_type_dao.query_all(['type_name'])
        cl = [mac_type.model_dump() for mac_type in mac_type_list]
        category_tree = CategoryService.gen_category_tree(cl)
        return category_tree

    @staticmethod
    def gen_category_tree(class_list):
        tree = CategoryTree(id=0, pid=-1, name="分类信息", show=True)
        temp = {tree.id: tree}

        for cls in class_list:
            category = temp.get(cls['type_id'])
            if category:
                category.id = cls['type_id']
                category.pid = cls['type_pid']
                category.name = cls['type_name']
                category.show = True if cls.get('type_status', 1) else False
            else:
                category = CategoryTree(id=cls['type_id'], pid=cls['type_pid'], name=cls['type_name'],
                                        show=True if cls.get('type_status', 1) else False)
                temp[cls['type_id']] = category

            parent = temp.get(category.pid)
            if not parent:
                parent = CategoryTree(id=cls['type_pid'], pid=0, name="",
                                      show=True if cls.get('type_status', 1) else False)
                temp[cls['type_pid']] = parent

            parent.children.append(category)

        return tree

    @staticmethod
    def save_mac_type(class_list):
        # 创建 TypeAdapter
        adapter = TypeAdapter(List[MacType])

        # 使用 TypeAdapter 验证和解析数据
        mac_type_list = adapter.validate_python(class_list)
        mac_type_dao.delete_items()
        mac_type_dao.upsert_items(mac_type_list)

        return mac_type_list

    @staticmethod
    def get_children_tree(id: int) -> Optional[List[CategoryTree]]:
        tree = CategoryService.get_category_tree_by_db()
        if not tree or not tree.children:
            return None
        for t in tree.children:
            if t.id == id:
                return t.children
        return None
