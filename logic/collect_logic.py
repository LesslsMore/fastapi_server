from service.system.collect_source import update_collect_source, del_collect_resource
from service.system.collect_source import find_collect_source_by_id
from model.system.collect_source import FilmSource, SourceGrade

class CollectLogic:
    @staticmethod
    def get_film_source(id: str):
        return find_collect_source_by_id(id)

    @staticmethod
    def update_film_source(fs: FilmSource) -> bool:
        return update_collect_source(fs)

    @staticmethod
    def del_film_source(id: str) -> bool:
        # 查找是否存在对应ID的站点信息
        s = find_collect_source_by_id(id)
        if s is None:
            raise ValueError("当前资源站信息不存在, 请勿重复操作")
        # 如果是主站点则返回提示禁止直接删除
        if s.grade == SourceGrade.MasterCollect:
            raise ValueError("主站点无法直接删除, 请先降级为附属站点再进行删除")
        # 删除采集源信息
        return del_collect_resource(id)