from model.collect.collect_source import SourceGrade, film_source_dao


class CollectLogic:

    @staticmethod
    def del_film_source(id: str) -> bool:
        # 查找是否存在对应ID的站点信息

        fs = film_source_dao.query_item(filter_dict={"id": id})
        if fs is None:
            raise ValueError("当前资源站信息不存在, 请勿重复操作")
        # 如果是主站点则返回提示禁止直接删除
        if fs.grade == SourceGrade.MasterCollect:
            raise ValueError("主站点无法直接删除, 请先降级为附属站点再进行删除")
        # 删除采集源信息

        film_source_dao.delete_item({"id": id})
        return True
