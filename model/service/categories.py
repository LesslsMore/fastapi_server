from typing import List, Optional
import json
from model.system.categories import CategoryTree
from plugin.db.redis_client import redis_client, init_redis_conn
from config import data_config

CATEGORY_TREE_KEY = getattr(data_config, 'CATEGORY_TREE_KEY', 'film:category:tree')
FILM_EXPIRED = getattr(data_config, 'FILM_EXPIRED', 3600 * 24 * 7)  # 默认一周

def save_category_tree(tree: CategoryTree) -> None:
    redis = redis_client or init_redis_conn()
    data = tree.json()
    redis.set(CATEGORY_TREE_KEY, data, ex=FILM_EXPIRED)

def get_category_tree() -> Optional[CategoryTree]:
    redis = redis_client or init_redis_conn()
    data = redis.get(CATEGORY_TREE_KEY)
    if not data:
        return None
    try:
        data_dict = json.loads(data)
        tree = CategoryTree(**data_dict)
        return tree
    except Exception:
        return None

def exists_category_tree() -> bool:
    redis = redis_client or init_redis_conn()
    return redis.exists(CATEGORY_TREE_KEY) == 1

def get_children_tree(id: int) -> Optional[List[CategoryTree]]:
    tree = get_category_tree()
    if not tree or not tree.children:
        return None
    for t in tree.children:
        if t.id == id:
            return t.children
    return None