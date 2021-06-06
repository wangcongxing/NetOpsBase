from rest_framework.routers import DefaultRouter
from django.urls import path, include

from app import views, modeExport

router = DefaultRouter()  # 可以处理视图的路由器

router.register(r'menu', views.MenuViewSet)  # 菜单管理
router.register(r'contenttype', views.ContentTypeViewSet)  # 内容类型管理
router.register(r'permission', views.PermissionViewSet)  # 权限管理
router.register(r'group', views.GroupViewSet)  # 权限组管理
router.register(r'user', views.UserViewSet)  # 用户管理
router.register(r'PeriodicTask', views.PeriodicTaskViewSet)  # 任务调度 PeriodicTask Celery 系统表
router.register(r'periodicTaskExport', modeExport.periodicTaskExport)  # 导出 PeriodicTask Celery 系统表
router.register(r'webSiteSet', views.webSiteSetViewSet)  # 网站设置
router.register(r'userInfo', views.userInfoViewSet)  # 用户信息
router.register(r'userInfoExport', modeExport.userInfoExport)  # 导出用户信息

urlpatterns = [
    # 默认数据初始化
    path('opsBaseInit', views.opsBaseInitDB.as_view()),
    # 获取token
    path('getAuthToken', views.LoginJWTAPIView.as_view()),
    path('checkAuthUser', views.CheckAuthUserAPIView.as_view()),

]

urlpatterns += router.urls
