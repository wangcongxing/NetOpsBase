from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission

# 参考实例
# https://blog.csdn.net/weixin_44984864/article/details/107376364
class PeriodicTaskPermission(BasePermission):
    def has_permission(self, request, view):
        """让所有用户都有权限"""
        print("has_permission=",request.user)
        return True

    def has_object_permission(self, request, view, obj):
        """用户是否有权限访问添加了权限控制类的数据对象"""
        # 需求：用户能够访问id为1，3的对象，其他的不能够访问
        if obj.id in (1, 3):
            return True
        else:
            return False
