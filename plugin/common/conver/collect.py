from model.collect.categories import CategoryTree


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