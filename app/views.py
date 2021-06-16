from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from app import models, modelFilters, modelSerializers, modelPermission
from utils import APIResponseResult
from utils.CustomViewBase import CustomViewBase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework.views import APIView
import os, uuid, time
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
# 定时任务
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
from datetime import datetime, timedelta
from django.db import transaction
from rest_framework import generics, mixins, views, viewsets
from django_filters import rest_framework as filters
import ast

# Create your views here.

# webSiteSet userInfo 只留下put方法
# 获取token时 同步新增userInfo
# init 新增默认网站设置数据webSiteSet
# 配置左侧菜单
# IntervalSchedule 数据存储异常的问题【seconds，5秒】

from django.core.cache import cache  # 引入缓存模块

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsBase import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsBase import test_settings as config
else:
    from NetOpsBase import settings as config


# 默认数据初始化
class opsBaseInitDB(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        # 初始化菜单 可考虑递归
        menujson = []
        with open(os.path.join(config.BASE_DIR, 'initConf', "menu.json"), "r") as f:
            menujson = json.load(f)
            print(menujson)
        for pitem in menujson:
            pname = pitem["name"]
            ptitle = pitem["title"]
            picon = pitem["icon"]
            psort = pitem["sort"]
            jump = pitem["jump"] if "jump" in pitem.keys() else ""

            plist = pitem["list"] if "list" in pitem.keys() else []
            pm, pc = models.Menu.objects.update_or_create(
                defaults={"name": pname, "title": ptitle, "icon": picon, "sort": psort, "url": jump,
                          'creator': 'admin',
                          'editor': 'admin'},
                name=pname)
            for citem in plist:
                cname = citem["name"]
                ctitle = citem["title"]
                cjump = citem["jump"] if "jump" in citem.keys() else ""
                clist = citem["list"] if "list" in citem.keys() else []
                csort = citem["sort"]
                cm, cc = models.Menu.objects.update_or_create(
                    defaults={"name": cname, "title": ctitle, "parent": pm, "url": cjump, "sort": csort,
                              'creator': 'admin', 'editor': 'admin'},
                    name=cname)
                for ccitem in clist:
                    ccname = ccitem["name"]
                    cctitle = ccitem["title"]
                    ccjump = ccitem["jump"]
                    ccsort = ccitem["sort"]
                    ccm, cc = models.Menu.objects.update_or_create(
                        defaults={"name": ccname, "title": cctitle, "parent": cm, "url": ccjump, "sort": ccsort,
                                  'creator': 'admin', 'editor': 'admin'},
                        name=ccname)

        # 权限组
        permissionGroup = ["超级管理员", "管理员", "纠错员", "采购员", "运营人员", "编辑员", "安全员", "网络组", "巡检员", "监控组", ]
        for gname in permissionGroup:
            models.Group.objects.update_or_create(defaults={"name": gname}, name=gname)
        # 系统用户
        # User.objects.delete()
        User.objects.update_or_create(
            defaults={'username': 'admin', 'is_staff': True, 'is_active': True, 'is_superuser': True,
                      'first_name': '管理员',
                      'password': make_password("admin@123")}, username='admin')
        # 网站设置
        models.webSiteSet.objects.update_or_create(
            defaults={'webName': "网络自动化", 'webUrl': 'http://www.netops.com', 'cacheTime': 10, 'uploadFileSize': 1024,
                      'fileExt': 'png|gif|jpg|jpeg|zip|rar', 'homeTitle': '网络自动化', 'META': 'H3c,huawei,ops,net,自动化',
                      'METADESC': 'NetOps 网络自动化系统解决方案，采用前后端分离开发模式 是目前非常流行的后台模板框架，广泛用于各类管理平台。',
                      'license': '© 2018 netops.com MIT license', 'creator': 'admin', 'editor': 'admin'}, id=1)

        # 调度任务
        # 创建10秒的间隔 interval 对象
        schedule, created = IntervalSchedule.objects.update_or_create(
            defaults={'every': 5, 'period': IntervalSchedule.SECONDS}, id=1)
        # 无参函数定时任务
        PeriodicTask.objects.update_or_create(defaults={'interval': schedule, 'name': '无参函数定时任务',
                                                        'task': 'celery_tasks.tasks.my_task2',
                                                        # 'expires': (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                                                        }, name='无参函数定时任务')
        # 创建带参数的任务
        PeriodicTask.objects.update_or_create(defaults={'interval': schedule, 'name': '有参函数定时任务',
                                                        'task': 'celery_tasks.tasks.my_task1',
                                                        'args': json.dumps([10, 20, 30]),
                                                        # 'expires': (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                                                        }, name='有参函数定时任务')
        # 第三方定时服务
        periodictask = PeriodicTask.objects.update_or_create(defaults={'interval': schedule, 'name': '第三方服务',
                                                                       'task': 'celery_tasks.tasks.sendUrl',
                                                                       # 'expires': (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                                                                       }, name='第三方服务')
        # 新增扩展类数据
        celeryextend, c = models.celeryExtend.objects.update_or_create(
            defaults={'periodictask': periodictask, 'tasktype': 1,
                      'url': 'http://127.0.0.1:7000/opsbase/app/opsBaseInit', 'reqmethod': 'GET',
                      'reqheaders': "{'Content-Type': 'application/json'}",
                      'proxies': "{'http': None,'https': None,}",
                      'payload': {}, 'phone': '19865875737', 'email': '2256807897@qq.com', 'creator': 'admin',
                      'editor': 'admin'}, id=1)

        resultArgs = []
        resultArgs.append(celeryextend.id)
        periodictask.args = resultArgs
        periodictask.save()

        return HttpResponse("<h1>数据库初始化成功</h1>")


class LoginJWTAPIView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        # username可能携带的不止是用户名，可能还是用户的其它唯一标识 手机号 邮箱
        print(request.GET)
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        if username is None or password is None:
            return APIResponseResult.APIResponse(-1, '用户名或密码不能为空!')
        user = User.objects.filter(username=username).first()
        if user is None:
            return APIResponseResult.APIResponse(-2, '用户名或密码输入有误')
        # 获得用户后，校验密码并签发token
        if not user.check_password(password):
            return APIResponseResult.APIResponse(-3, '密码错误')
        # 更新最后一次登录时间
        user.last_login = datetime.now()
        user.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return APIResponseResult.APIResponse(0, 'ok', results={
            'username': user.username,
            'access_token': token
        })


class CheckAuthUserAPIView(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        print(request.user)
        print(type(request.user))
        if type(request.user) == dict:
            username = request.user["username"]
        else:
            username = request.user.username
        currentUser = User.objects.filter(username=username).first()
        username = "游客身份"
        if currentUser and currentUser.username:
            username = currentUser.username
        return APIResponseResult.APIResponse(0, 'ok', results={
            "username": username
            , "sex": "男"
            , "role": 1,
        })


# 系统左侧菜单管理

def get_child_menu(childs):
    children = []
    if childs:
        for child in childs:
            data = {"name": child.name, "title": child.title, "icon": child.icon, "jump": child.url, "list": []}
            _childs = models.Menu.objects.filter(parent=child)
            if _childs:
                data["list"] = get_child_menu(_childs)
            children.append(data)
    return children


class MenuViewSet(CustomViewBase):
    queryset = models.Menu.objects.all().order_by('sort')
    serializer_class = modelSerializers.MenuSerializer

    # 返回菜单上下级关系
    @action(methods=['get', 'post'], detail=False, url_path='parent_menu')
    def parent_menu(self, request, *args, **kwargs):
        firstmenus = models.Menu.objects.order_by('parent', 'sort')
        menus = []
        for item in firstmenus:
            title_list = [item.title]
            p = item.parent
            while p:
                title_list.insert(0, p.title)
                p = p.parent
            menus.append({"value": item.id, "title": '/'.join(title_list)})

        return APIResponseResult.APIResponse(0, 'ok', results=menus)

    # 返回左侧菜单
    @action(methods=['get', 'post'], detail=False, url_path='left_menu')
    def left_menu(self, request, *args, **kwargs):
        # 获得用户权限
        if type(request.user) == dict:
            username = request.user["username"]
        else:
            username = request.user.username
        tree = []
        currentUser = User.objects.filter(username=username).first()
        if currentUser.is_superuser:
            firstmenus = models.Menu.objects.filter(parent=None).order_by('sort')
        else:
            user_permission_id = []
            group_permission_id = []
            current_user_group = Group.objects.filter(user__username=currentUser)
            print("current_group_set", current_user_group)
            current_user_permissions = Permission.objects.filter(user__username=currentUser)
            print("current_user_permissions", current_user_permissions)
            print("get_user_permissions>", currentUser.get_user_permissions())
            print("get_group_permissions>", currentUser.get_group_permissions())
            for up in current_user_group:
                group_permission_id.append(up.id)
            for gp in current_user_permissions:
                user_permission_id.append(gp.id)
            print("user_permission_id", user_permission_id)
            print("group_permission_id", group_permission_id)
            # 查询可以操作的菜单
            firstmenus = models.Menu.objects.filter(Q(group__id__in=group_permission_id) |
                                                    Q(permission__id__in=user_permission_id),
                                                    parent=None).distinct().order_by('sort')
        # print(menus.query)
        for menu in firstmenus:
            menu_data = {"name": menu.name, "title": menu.title, "icon": menu.icon, "jump": menu.url}
            childs = models.Menu.objects.filter(parent=menu).order_by('sort')
            if childs:
                menu_data["list"] = get_child_menu(childs)
            tree.append(menu_data)
        # tree = [x for x in tree if x["list"] != []]
        return APIResponseResult.APIResponse(0, 'success', results=tree)


class ContentTypeViewSet(CustomViewBase):
    queryset = ContentType.objects.all().order_by('id')
    serializer_class = modelSerializers.ContentTypeSerializer


class PermissionViewSet(CustomViewBase):
    queryset = Permission.objects.all().order_by('id')
    serializer_class = modelSerializers.PermissionSerializer


class GroupViewSet(CustomViewBase):
    queryset = Group.objects.all().order_by('id')
    serializer_class = modelSerializers.GroupSerializer


class UserViewSet(CustomViewBase):
    queryset = User.objects.all().order_by('-username')
    serializer_class = modelSerializers.UserSerializer
    filter_class = modelFilters.UserFilter
    ordering_fields = ('id', 'date_joined')  # 排序

    # 修改密码
    @action(methods=['put'], detail=False, url_path='resetPassWord')
    def resetPassWord(self, request, *args, **kwargs):
        oldPassword = request.data.get("oldPassword", None)
        if type(request.user) == dict:
            username = request.user["username"]
        else:
            username = request.user.username
        currentUser = User.objects.filter(username=username).first()
        if not currentUser.check_password(oldPassword):
            return APIResponseResult.APIResponse(-1, '当前密码输入错误')
        password = request.data.get("password", None)
        repassword = request.data.get("repassword", None)
        if password != repassword:
            return APIResponseResult.APIResponse(-2, '新密码和确认新密码输入不一致')

        currentUser.password = make_password(password)
        currentUser.save()
        return APIResponseResult.APIResponse(0, '修改成功')

    # 修改用户信息
    @action(methods=['put'], detail=False, url_path='resetUserInfo')
    def resetUserInfo(self, request, *args, **kwargs):
        pass


class PeriodicTaskViewSet(CustomViewBase):
    queryset = PeriodicTask.objects.all().order_by('-id')
    serializer_class = modelSerializers.PeriodicTaskSerializer
    filter_class = modelFilters.PeriodicTaskFilter
    ordering_fields = ('id', 'expires')  # 排序
    permission_classes = [modelPermission.PeriodicTaskPermission]

    # 修改状态
    @action(methods=['put'], detail=False, url_path='resetEnabled')
    def resetEnabled(self, request, *args, **kwargs):
        nid = request.data.get('nid', None)
        if nid is None:
            return APIResponseResult.APIResponse(-1, '请求发生错误,请稍后再试!')
        periodictask = PeriodicTask.objects.filter(id=nid).first()
        if periodictask is None:
            return APIResponseResult.APIResponse(-2, '请求数据不存在,请稍后再试!')
        periodictask.enabled = False if periodictask.enabled else True
        periodictask.save()
        return APIResponseResult.APIResponse(0, "已启用" if periodictask.enabled else "已禁用")


class webSiteSetViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.webSiteSet.objects.all().order_by('-id')
    serializer_class = modelSerializers.webSiteSetSerializer

    def list(self, request, *args, **kwargs):
        websiteinfo = models.webSiteSet.objects.all().values().order_by('-id')[0]
        return APIResponseResult.APIResponse(0, 'success', results=websiteinfo, http_status=status.HTTP_200_OK, )


class userInfoViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.userInfo.objects.all().order_by('-id')
    serializer_class = modelSerializers.userInfoSerializer

    def list(self, request, *args, **kwargs):
        if type(request.user) == dict:
            username = request.user["username"]
        else:
            username = request.user.username

        obj = models.userInfo.objects.filter(creator=username).first()
        if obj is None:
            obju, created = models.userInfo.objects.update_or_create(
                defaults={"user": obj, "nickName": obj.get_full_name(), "email": obj.email,
                          'creator': obj.username, 'editor': obj.username},
                user=obj)

        results = {}
        results.update({"id": obj.id})
        results.update({"nickName": obj.nickName})
        results.update({"sex": obj.sex})
        results.update({"avatar": obj.avatar.name})
        results.update({"phone": obj.phone})
        results.update({"email": obj.email})
        results.update({"desc": obj.desc})
        results.update({"roles": [{}]})
        results.update({"username": username})
        return APIResponseResult.APIResponse(0, 'success', results=results, http_status=status.HTTP_200_OK, )
