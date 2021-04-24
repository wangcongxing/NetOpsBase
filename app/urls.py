from rest_framework.routers import DefaultRouter
from django.urls import path, include

from app import views

router = DefaultRouter()  # 可以处理视图的路由器

router.register(r'menu', views.MenuViewSet)
router.register(r'contenttype', views.ContentTypeViewSet)
router.register(r'permission', views.PermissionViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'user', views.UserViewSet)

urlpatterns = [

    # 获取token
    path('getAuthToken', views.LoginJWTAPIView.as_view()),
    path('checkAuthUser', views.CheckAuthUserAPIView.as_view()),

]

urlpatterns += router.urls
