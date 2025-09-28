import json
import logging

from dao.collect.category import CategoryService
from dao.collect.kv_dao import KVModel
from model.collect.mac.type import mac_type_dao


def test_gen_category_tree():
    class_list = json.loads("""
    [
{
"type_id": 1,
"type_pid": 0,
"type_name": "国产动漫"
},
{
"type_id": 2,
"type_pid": 0,
"type_name": "日韩动漫"
},
{
"type_id": 3,
"type_pid": 0,
"type_name": "欧美动漫"
},
{
"type_id": 4,
"type_pid": 0,
"type_name": "港台动漫"
},
{
"type_id": 5,
"type_pid": 0,
"type_name": "动漫电影"
},
{
"type_id": 6,
"type_pid": 0,
"type_name": "里番动漫"
},
{
"type_id": 7,
"type_pid": 0,
"type_name": "电影"
},
{
"type_id": 8,
"type_pid": 0,
"type_name": "连续剧"
},
{
"type_id": 9,
"type_pid": 0,
"type_name": "综艺"
},
{
"type_id": 10,
"type_pid": 7,
"type_name": "动作片"
},
{
"type_id": 11,
"type_pid": 7,
"type_name": "喜剧片"
},
{
"type_id": 12,
"type_pid": 7,
"type_name": "爱情片"
},
{
"type_id": 13,
"type_pid": 7,
"type_name": "科幻片"
},
{
"type_id": 14,
"type_pid": 7,
"type_name": "恐怖片"
},
{
"type_id": 15,
"type_pid": 7,
"type_name": "剧情片"
},
{
"type_id": 16,
"type_pid": 7,
"type_name": "战争片"
},
{
"type_id": 17,
"type_pid": 7,
"type_name": "惊悚片"
},
{
"type_id": 18,
"type_pid": 7,
"type_name": "家庭片"
},
{
"type_id": 19,
"type_pid": 7,
"type_name": "古装片"
},
{
"type_id": 20,
"type_pid": 7,
"type_name": "历史片"
},
{
"type_id": 21,
"type_pid": 7,
"type_name": "悬疑片"
},
{
"type_id": 22,
"type_pid": 7,
"type_name": "犯罪片"
},
{
"type_id": 23,
"type_pid": 7,
"type_name": "灾难片"
},
{
"type_id": 24,
"type_pid": 7,
"type_name": "记录片"
},
{
"type_id": 25,
"type_pid": 7,
"type_name": "短片"
},
{
"type_id": 26,
"type_pid": 8,
"type_name": "国产剧"
},
{
"type_id": 27,
"type_pid": 8,
"type_name": "香港剧"
},
{
"type_id": 28,
"type_pid": 8,
"type_name": "韩国剧"
},
{
"type_id": 29,
"type_pid": 8,
"type_name": "欧美剧"
},
{
"type_id": 30,
"type_pid": 8,
"type_name": "台湾剧"
},
{
"type_id": 31,
"type_pid": 8,
"type_name": "日本剧"
},
{
"type_id": 32,
"type_pid": 8,
"type_name": "海外剧"
},
{
"type_id": 33,
"type_pid": 8,
"type_name": "泰国剧"
},
{
"type_id": 34,
"type_pid": 9,
"type_name": "大陆综艺"
},
{
"type_id": 35,
"type_pid": 9,
"type_name": "港台综艺"
},
{
"type_id": 36,
"type_pid": 9,
"type_name": "日韩综艺"
},
{
"type_id": 37,
"type_pid": 9,
"type_name": "欧美综艺"
},
{
"type_id": 38,
"type_pid": 8,
"type_name": "短剧"
},
{
"type_id": 39,
"type_pid": 7,
"type_name": "伦理片"
}
]
    """)
    tree = CategoryService.save_mac_type(class_list)
    print(tree)
    assert tree


def test_delete_items():
    mac_type_dao.delete_items()
    print('')
    assert True


def test_query_all():
    items = mac_type_dao.query_all(['type_name'])
    print(items)
    assert len(items) == 0


def test_get_category_tree():
    category_tree = CategoryService.get_category_tree_by_db()
    logging.info(category_tree)


def test_get_children_tree():
    res = CategoryService.get_children_tree(4)
    logging.info(res)


def test():
    # 检查表结构是否一致
    from sqlalchemy.inspection import inspect
    logging.info(inspect(KVModel).unique_constraints)  # 应输出 [UniqueConstraint('key')]
