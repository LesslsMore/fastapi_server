from typing import List, Optional
import json

from config.data_config import CATEGORY_TREE_KEY, FILM_EXPIRED
from model.system.categories import CategoryTree
from plugin.db import redis_client


def save_category_tree(tree: CategoryTree) -> None:
    try:
        data = tree.json()
        redis_client.set(CATEGORY_TREE_KEY, data, ex=FILM_EXPIRED)
    except Exception as err:
        print(f"SaveCategoryTree Error: {err}")


def get_category_tree() -> Optional[CategoryTree]:
    data = redis_client.get(CATEGORY_TREE_KEY)
    if not data:
        return None
    try:
        data_dict = json.loads(data)
        tree = CategoryTree(**data_dict)
        return tree
    except Exception:
        return None


def exists_category_tree() -> bool:
    return redis_client.exists(CATEGORY_TREE_KEY) == 1


def get_children_tree(id: int) -> Optional[List[CategoryTree]]:
    tree = get_category_tree()
    if not tree or not tree.children:
        return None
    for t in tree.children:
        if t.id == id:
            return t.children
    return None
