import json

from model.collect.categories import CategoryTree
from dao.collect.kv_dao import KVModel
from dao.collect.categories import CategoryTreeService


def test_save_category_tree():
    category_tree = CategoryTree(**json.loads('''
    {"id":0,"pid":-1,"name":"分类信息","show":true,"children":[{"id":1,"pid":0,"name":"电影片","show":true,"children":[{"id":6,"pid":1,"name":"动作片","show":true,"children":null},{"id":7,"pid":1,"name":"喜剧片","show":true,"children":null},{"id":8,"pid":1,"name":"爱情片","show":true,"children":null},{"id":9,"pid":1,"name":"科幻片","show":true,"children":null},{"id":10,"pid":1,"name":"恐怖片","show":true,"children":null},{"id":11,"pid":1,"name":"剧情片","show":true,"children":null},{"id":12,"pid":1,"name":"战争片","show":true,"children":null},{"id":20,"pid":1,"name":"记录片","show":true,"children":null},{"id":34,"pid":1,"name":"伦理片","show":true,"children":null},{"id":45,"pid":1,"name":"预告片","show":true,"children":null}]},{"id":2,"pid":0,"name":"连续剧","show":true,"children":[{"id":13,"pid":2,"name":"国产剧","show":true,"children":null},{"id":14,"pid":2,"name":"香港剧","show":true,"children":null},{"id":15,"pid":2,"name":"韩国剧","show":true,"children":null},{"id":16,"pid":2,"name":"欧美剧","show":true,"children":null},{"id":21,"pid":2,"name":"台湾剧","show":true,"children":null},{"id":22,"pid":2,"name":"日本剧","show":true,"children":null},{"id":23,"pid":2,"name":"海外剧","show":true,"children":null},{"id":24,"pid":2,"name":"泰国剧","show":true,"children":null},{"id":46,"pid":2,"name":"短剧","show":true,"children":null}]},{"id":3,"pid":0,"name":"综艺片","show":true,"children":[{"id":25,"pid":3,"name":"大陆综艺","show":true,"children":null},{"id":26,"pid":3,"name":"港台综艺","show":true,"children":null},{"id":27,"pid":3,"name":"日韩综艺","show":true,"children":null},{"id":28,"pid":3,"name":"欧美综艺","show":true,"children":null}]},{"id":4,"pid":0,"name":"动漫片","show":true,"children":[{"id":29,"pid":4,"name":"国产动漫","show":true,"children":null},{"id":30,"pid":4,"name":"日韩动漫","show":true,"children":null},{"id":31,"pid":4,"name":"欧美动漫","show":true,"children":null},{"id":32,"pid":4,"name":"港台动漫","show":true,"children":null},{"id":33,"pid":4,"name":"海外动漫","show":true,"children":null}]},{"id":35,"pid":0,"name":"电影解说","show":true,"children":null},{"id":36,"pid":0,"name":"体育","show":true,"children":[{"id":37,"pid":36,"name":"足球","show":true,"children":null},{"id":38,"pid":36,"name":"篮球","show":true,"children":null},{"id":39,"pid":36,"name":"网球","show":true,"children":null},{"id":40,"pid":36,"name":"斯诺克","show":true,"children":null}]},{"id":41,"pid":0,"name":"演员","show":true,"children":null},{"id":42,"pid":0,"name":"新闻资讯","show":true,"children":[{"id":43,"pid":42,"name":"电影资讯","show":true,"children":null},{"id":44,"pid":42,"name":"娱乐新闻","show":true,"children":null}]}]}
    '''))
    CategoryTreeService.save_category_tree(category_tree)

def test_get_category_tree():
    category_tree = CategoryTreeService.get_category_tree()
    print(category_tree)

def test_exists_category_tree():
    res = CategoryTreeService.exists_category_tree()
    print(res)

def test_get_children_tree():
    res = CategoryTreeService.get_children_tree(4)
    print(res)


def test():
    # 检查表结构是否一致
    from sqlalchemy.inspection import inspect
    print(inspect(KVModel).unique_constraints)  # 应输出 [UniqueConstraint('key')]