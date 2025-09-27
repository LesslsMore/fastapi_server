from typing import List, Optional

from pydantic import BaseModel


# 分类信息
class Category(BaseModel):
    id: Optional[int] = None
    pid: Optional[int] = None
    Pid: Optional[int] = None
    name: Optional[str] = None
    show: Optional[bool] = None


# 分类信息树形结构
class CategoryTree(Category):
    children: Optional[List['CategoryTree']] = []

    def find_by_id(self, target_id: int) -> Optional['CategoryTree']:
        """
        在当前节点及其子树中查找指定ID的节点

        Args:
            target_id: 要查找的节点ID

        Returns:
            找到的节点或None
        """
        # 检查当前节点
        if self.id == target_id:
            return self

        # 递归检查子节点
        if self.children:
            for child in self.children:
                result = child.find_by_id(target_id)
                if result:
                    return result

        return None


CategoryTree.update_forward_refs()
