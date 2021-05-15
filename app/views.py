from django.db import transaction
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework import viewsets, serializers, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from app import models
from utils import APIResponseResult
from utils.CustomViewBase import CustomViewBase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework.views import APIView
import os, uuid
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.hashers import make_password
# Create your views here.


from django.core.cache import cache  # 引入缓存模块

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsBase import pro_settings as config
elif ENV_PROFILE == "test":
    from NetOpsBase import test_settings as config
else:
    from NetOpsBase import settings as config


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


class MenuSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)
    parentmenu = serializers.SerializerMethodField()

    def get_parentmenu(self, obj):
        title_list = [obj.title, ]
        p = obj.parent
        while p:
            # caption_list.append(p.caption)
            title_list.insert(0, p.title)
            p = p.parent
        return "-".join(title_list)

    def create(self, validated_data):
        username = self.context["request"].user["username"]
        validated_data.update({"creator": username, "editor": username})
        if "parent" in self.initial_data and self.initial_data["parent"]:
            validated_data.update({"parent_id": int(self.initial_data["parent"])})
        objmenu = models.Menu.objects.create(**validated_data)

        print(validated_data)

        # 添加组
        groupinfo = filter(None, str(self.initial_data["groupinfo"]).split(','))
        for p in groupinfo:
            objmenu.group.add(Group.objects.filter(id=int(p)).first())

        # 添加权限
        permissioninfo = filter(None, str(self.initial_data["permissioninfo"]).split(','))
        for p in permissioninfo:
            objmenu.permission.add(Permission.objects.filter(id=int(p)).first())

        return objmenu

    # def update(self, instance, validated_data):
    #     print("instance===", instance)
    #     instance.save()
    #     return instance

    class Meta:
        model = models.Menu
        fields = ["id", "title", "name", "url", "sort", "icon", "parent", "parentmenu", "group", "permission", "desc"]
        depth = 1


# 系统左侧菜单管理
class MenuViewSet(CustomViewBase):
    queryset = models.Menu.objects.all().order_by('-id')
    serializer_class = MenuSerializer

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
            menus.append({"value": item.id, "title": '>>'.join(title_list)})

        return APIResponseResult.APIResponse(0, 'ok', results=menus)

    # 返回左侧菜单
    @action(methods=['get', 'post'], detail=False, url_path='left_menu')
    def left_menu(self, request, *args, **kwargs):
        # 获得用户权限
        print(request.user)
        print(type(request.user))
        if type(request.user) == dict:
            username = request.user["username"]
        else:
            username = request.user.username
        current_url = request.path_info
        print("current_url>", current_url)
        print(username)
        # 当前用户的权限
        currentUser = User.objects.filter(username=username).first()
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
        # 绑定一级菜单
        leftmenu = {}
        firstmenus = models.Menu.objects.filter(parent=None).order_by('sort')
        for fmenu in firstmenus:
            leftmenu.update(
                {fmenu.name: {"title": fmenu.title, "icon": "layui-icon-home", "sort": fmenu.sort, "list": []}})
        # 查询可以操作的菜单
        menus = models.Menu.objects.filter(Q(group__id__in=group_permission_id) |
                                           Q(permission__id__in=user_permission_id),
                                           parent__isnull=False).distinct().order_by('sort')
        print(menus.query)
        print("menus", len(menus))
        for item in menus:
            print("item.title", item.title)
            children_menu_list = []
            children = item.get_children()
            print("children==", children)
            for cmenu in children:
                children_menu_list.append({"name": cmenu.name, "title": cmenu.title, "jump": cmenu.url})
            print(children_menu_list)
            # 根据子权限获取父级菜单名称
            p = item.parent
            while p:
                # caption_list.append(p.caption)
                print("p.title", p.title)
                if p.name in leftmenu:
                    children_menu_list.append({"name": item.name, "title": item.title, "jump": item.url})
                # 可实现递归获取,如有需要可自行扩展
                p = p.parent
            if item.parent is None:
                leftmenu.get(item.name)["list"] = children_menu_list
            else:
                leftmenu.get(item.parent.name)["list"] += children_menu_list

        listmenu = []
        for key, value in leftmenu.items():
            if len(value["list"]):
                listmenu.append(value)

        print("leftmenu==>", leftmenu)
        print("listmenu==>", listmenu)
        return APIResponseResult.APIResponse(0, 'success', results=listmenu)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        res = serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if res:
            instance.permission.clear()
            permissioninfo = filter(None, str(request.data["permissioninfo"]).split(','))
            for p in permissioninfo:
                instance.permission.add(Permission.objects.filter(id=int(p)).first())

            # 添加组
            instance.group.clear()
            groupinfo = filter(None, str(request.data["groupinfo"]).split(','))
            for p in groupinfo:
                instance.group.add(Group.objects.filter(id=int(p)).first())

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponseResult.APIResponse(0, 'success', results=serializer.data,
                                             http_status=status.HTTP_200_OK, )


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        title = request.data.get("title", None)
        if title and title != "":
            queryset = queryset.filter(title__contains=title)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )


# 系统ContentType管理
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'
        depth = 1


class ContentTypeViewSet(CustomViewBase):
    queryset = ContentType.objects.all().order_by('-id')
    serializer_class = ContentTypeSerializer


# 系统权限菜单管理
class PermissionSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        app_label = self.initial_data["app_label"]
        model_name = self.initial_data["model_name"]

        content_type = ContentType.objects.create(app_label=app_label, model=model_name)

        validated_data.update({"content_type_id": content_type.id})
        print(validated_data)
        return Permission.objects.create(**validated_data)

    class Meta:
        model = Permission
        fields = '__all__'
        depth = 1


class PermissionViewSet(CustomViewBase):
    queryset = Permission.objects.filter(id__gt=28).order_by('-id')
    serializer_class = PermissionSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        res = serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if res:
            app_label = request.data["app_label"]
            model_name = request.data["model_name"]
            instance.content_type.app_label = app_label
            instance.content_type.model = model_name
            instance.content_type.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.data.get("name", None)
        if name and name != "":
            queryset = queryset.filter(name__contains=name)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        with transaction.atomic():
            try:
                instance.content_type.delete()
                self.perform_destroy(instance)
            except Exception as ex:
                transaction.rollback()
                raise ex
        return APIResponseResult.APIResponse(0, 'success',
                                             http_status=status.HTTP_200_OK, )


# 系统组菜单管理
class GroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        objGroup = Group.objects.create(**validated_data)
        permissioninfo = filter(None, str(self.initial_data["permissioninfo"]).split(','))
        for p in permissioninfo:
            objGroup.permissions.add(Permission.objects.filter(id=int(p)).first())
        return objGroup

    class Meta:
        model = Group
        fields = '__all__'
        depth = 1


class GroupViewSet(CustomViewBase):
    queryset = Group.objects.all().order_by('-id')
    serializer_class = GroupSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        res = serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if res:
            instance.permissions.clear()
            permissioninfo = filter(None, str(request.data["permissioninfo"]).split(','))
            for p in permissioninfo:
                instance.permissions.add(Permission.objects.filter(id=int(p)).first())

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        with transaction.atomic():
            try:
                instance.permissions.clear()
                self.perform_destroy(instance)
            except Exception as ex:
                transaction.rollback()
                raise ex
        return APIResponseResult.APIResponse(0, 'delete resource success', results=[],
                                             http_status=status.HTTP_200_OK, )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.data.get("name", None)
        if name and name != "":
            queryset = queryset.filter(name__contains=name)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )


# 系统权限菜单管理
class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        password = self.initial_data["password"]
        if "is_staff" in self.initial_data:
            validated_data.update({"is_staff": self.initial_data["is_staff"]})
        if "is_active" in self.initial_data:
            validated_data.update({"is_active": self.initial_data["is_active"]})
        if "is_superuser" in self.initial_data:
            validated_data.update({"is_superuser": self.initial_data["is_superuser"]})
        # 随机密码 仅用于ad域认证
        if "password" in self.initial_data:

            validated_data.update({"password": make_password(password)})
        else:
            validated_data.update({"password": make_password(str(uuid.uuid4()))})
        cuser = User.objects.create(**validated_data)

        # 添加组
        groupinfo = filter(None, str(self.initial_data["groupinfo"]).split(','))
        for p in groupinfo:
            cuser.groups.add(Group.objects.filter(id=int(p)).first())

        # 添加权限
        permissioninfo = filter(None, str(self.initial_data["permissioninfo"]).split(','))
        for p in permissioninfo:
            cuser.user_permissions.add(Permission.objects.filter(id=int(p)).first())

        return cuser

    # def update(self, instance, validated_data):
    #     pass

    class Meta:
        model = User
        fields = ["id","username", "first_name", "last_name", "email", "groups", "user_permissions", "is_staff", "is_active",
                  "is_superuser", "date_joined", "last_login"]
        depth = 3


class UserViewSet(CustomViewBase):
    queryset = User.objects.all().order_by('-username')
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = User.objects.filter(username=request.data["username"]).first()  # self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        res = serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if res:
            instance.user_permissions.clear()
            permissioninfo = filter(None, str(request.data["permissioninfo"]).split(','))
            for p in permissioninfo:
                instance.user_permissions.add(Permission.objects.filter(id=int(p)).first())

            # 添加组
            instance.groups.clear()
            groupinfo = filter(None, str(request.data["groupinfo"]).split(','))
            for p in groupinfo:
                instance.groups.add(Group.objects.filter(id=int(p)).first())

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponseResult.APIResponse(0, 'success', results=serializer.data,
                                             http_status=status.HTTP_200_OK, )


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        username = request.data.get("username", None)
        if username and username != "":
            queryset = queryset.filter(username__contains=username)

        first_name = request.data.get("first_name", None)
        if first_name:
            queryset = queryset.filter(first_name__contains=first_name)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )
