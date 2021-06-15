# 用于设置model serializers
from rest_framework import viewsets, serializers, status
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import os, uuid, time, random
from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from app import models

# 定时任务时间参数 主要用于验证前端传到后台的数据是否合法
IntervalScheduleDict = {"DAYS": [IntervalSchedule.DAYS, "天"],
                        "HOURS": [IntervalSchedule.HOURS, "时"],
                        "MINUTES": [IntervalSchedule.MINUTES, "分"],
                        "SECONDS": [IntervalSchedule.SECONDS, "秒"],
                        "MICROSECONDS": [IntervalSchedule.MICROSECONDS, "微秒"], }


class PeriodicTaskSerializer(serializers.ModelSerializer):
    intervalshow = serializers.SerializerMethodField()
    intervaldict = serializers.SerializerMethodField()
    celeryextend = serializers.SerializerMethodField()

    def get_intervalshow(self, obj):
        if obj.interval:
            return "每{}{}运行/次".format(str(obj.interval.every),
                                      IntervalScheduleDict[str(obj.interval.period).upper()][1])
        else:
            return "空"

    def get_intervaldict(self, obj):
        if obj.interval:
            return [obj.interval.every, obj.interval.period]
        else:
            return []

    def get_celeryextend(self, obj):
        return models.celeryExtend.objects.filter(periodictask=obj).values()

    # 新增任务
    def create(self, validated_data):
        username = self.context["request"].user["username"]
        name = str(self.initial_data.get("name", "")).strip()
        tasktype = str(self.initial_data.get("tasktype", "")).strip()
        task = str(self.initial_data.get("task", "")).strip()
        intervalType = str(self.initial_data.get("intervalType", "")).strip()
        args = str(self.initial_data.get("args", [])).strip()
        kwargs = str(self.initial_data.get("kwargs", [])).strip()
        url = str(self.initial_data.get("url", "")).strip()
        # 不知道为何选择Get 获取到的数据 前面会有\b
        reqmethod = str(self.initial_data.get("reqmethod", "")).replace("\b", "").strip()
        reqheaders = str(self.initial_data.get("reqheaders", "")).strip()
        payload = str(self.initial_data.get("payload", "")).strip()
        runtime = int(str(self.initial_data.get("runtime", "")).strip())
        start_time = str(self.initial_data.get("start_time", "")).strip()
        expires = str(self.initial_data.get("expires", "")).strip()
        phone = str(self.initial_data.get("phone", "")).strip()
        email = str(self.initial_data.get("email", "")).strip()
        description = str(self.initial_data.get("description", "")).strip()
        if intervalType not in IntervalScheduleDict:
            print("intervalType=", intervalType)
            pass
        print("intervalType 0", IntervalScheduleDict[intervalType][0])
        intervalschedule = IntervalSchedule.objects.create(every=runtime, period=IntervalScheduleDict[intervalType][0])
        taskState = PeriodicTask.objects.filter(name=name).count()
        if taskState == 0:
            name = name + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with transaction.atomic():
            periodictask = PeriodicTask.objects.create(interval=intervalschedule, name=name,
                                                       task=task,
                                                       args=args,
                                                       kwargs=kwargs,
                                                       start_time=start_time,
                                                       expires=expires,
                                                       description=description)
            # 新增扩展类数据
            celeryextend = models.celeryExtend.objects.create(periodictask=periodictask, tasktype=tasktype, url=url,
                                                              reqmethod=reqmethod,
                                                              reqheaders=reqheaders,
                                                              payload=payload, phone=phone, email=email,
                                                              creator=username,
                                                              editor=username)
            if tasktype == "1":
                resultArgs = []
                resultArgs.append(celeryextend.id)
                periodictask.args = resultArgs
                periodictask.save()

        print("periodictask={}".format(periodictask))
        return periodictask

    # 修改任务
    def update(self, instance, validated_data):
        username = self.context["request"].user["username"]
        intervalType = str(self.initial_data.get("intervalType", "")).strip()
        url = str(self.initial_data.get("url", "")).strip()
        # 不知道为何选择Get 获取到的数据 前面会有\b
        reqmethod = str(self.initial_data.get("reqmethod", "")).replace("\b", "").strip()
        reqheaders = str(self.initial_data.get("reqheaders", "")).strip()
        proxies = str(self.initial_data.get("proxies", "")).strip()
        payload = str(self.initial_data.get("payload", "")).strip()
        runtime = int(str(self.initial_data.get("runtime", "")).strip())
        phone = str(self.initial_data.get("phone", "")).strip()
        email = str(self.initial_data.get("email", "")).strip()
        if intervalType == "":
            print("----如何返回提示信息")
            return False
        with transaction.atomic():
            # 修改计时器
            interval = IntervalSchedule.objects.get(id=instance.interval.id)
            interval.every = runtime
            interval.period = IntervalScheduleDict[intervalType][0]
            interval.save()
            # 修改扩展属性类 任务是第三方扩展服务的时候在执行修改操作
            if self.initial_data['tasktype'] == '1':
                celeryextend = models.celeryExtend.objects.filter(periodictask=instance).first()
                celeryextend.url = url
                celeryextend.reqmethod = reqmethod
                celeryextend.reqheaders = reqheaders
                celeryextend.proxies = proxies
                celeryextend.payload = payload
                celeryextend.phone = phone
                celeryextend.email = email
                celeryextend.editor = username
                celeryextend.save()
            # 修改计划任务
            validated_data["enabled"] = True
            obj = super().update(instance, validated_data)
            return obj

    class Meta:

        model = PeriodicTask
        fields = ["id", "name", "task", "args", "kwargs", "queue", "exchange", "routing_key",
                  "headers", "priority", "expires", "expire_seconds", "one_off", "start_time",
                  "enabled", "last_run_at", "total_run_count", "date_changed", "description", "interval",
                  "intervalshow", "intervaldict", "celeryextend", "crontab", "solar", "clocked"]
        # depth = 3


class PeriodicTaskExportSerializer(serializers.ModelSerializer):
    one_off_show = serializers.SerializerMethodField()
    intervalshow = serializers.SerializerMethodField()

    def get_intervalshow(self, obj):
        if obj.interval:
            return "每{}{}运行/次".format(str(obj.interval.every),
                                      IntervalScheduleDict[str(obj.interval.period).upper()][1])
        else:
            return "空"

    def get_one_off_show(self, obj):
        if obj.one_off:
            return "否"
        else:
            return "是"

    class Meta:

        model = PeriodicTask
        fields = ["id", "name", "task", "args", "kwargs", "queue", "exchange", "routing_key",
                  "headers", "priority", "expires", "expire_seconds", "one_off_show", "start_time",
                  "enabled", "last_run_at", "total_run_count", "date_changed", "description", "intervalshow",
                  "crontab", "solar", "clocked"]


# 网站设置实体化
class webSiteSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.webSiteSet
        fields = "__all__"


# 系统权限菜单管理
class UserSerializer(serializers.ModelSerializer):
    extuserinfo = serializers.SerializerMethodField()

    def get_extuserinfo(self, obj):
        return models.userInfo.objects.filter(creator=obj.username).values("phone", "desc").first()

    def create(self, validated_data):
        if "is_staff" in validated_data:
            validated_data.update({"is_staff": validated_data["is_staff"]})
        if "is_active" in validated_data:
            validated_data.update({"is_active": validated_data["is_active"]})
        if "is_superuser" in validated_data:
            validated_data.update({"is_superuser": validated_data["is_superuser"]})
        # 随机密码
        password = "admin@123"  # str(random.randint(0,99999999)).zfill(8)
        validated_data.update({"password": make_password(password)})
        cuser = User.objects.create(**validated_data)
        # 添加组
        groupinfo = filter(None, str(self.initial_data["groupinfo"]).split(','))
        for p in groupinfo:
            cuser.groups.add(Group.objects.filter(id=int(p)).first())
        # 添加权限
        permissioninfo = filter(None, str(self.initial_data["permissioninfo"]).split(','))
        for p in permissioninfo:
            cuser.user_permissions.add(Permission.objects.filter(id=int(p)).first())
        # 手机号码 需要验证格式并加密存储
        phone = self.initial_data["phone"]
        desc = self.initial_data["desc"]
        models.userInfo.objects.update_or_create(
            defaults={"nickName": cuser.get_full_name(), "phone": phone, "email": cuser.email, "desc": desc},
            creator=cuser.username)

        return cuser

    # 修改用户信息
    def update(self, instance, validated_data):
        if "is_staff" in validated_data:
            instance.is_staff = validated_data["is_staff"]
        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]
        if "is_superuser" in validated_data:
            instance.is_superuser = validated_data["is_superuser"]
        # 添加组
        instance.groups.clear()
        ginfo = self.initial_data["groupinfo"]
        groupinfo = filter(None, str(ginfo).split(','))
        for p in groupinfo:
            instance.groups.add(Group.objects.filter(id=int(p)).first())

        pinfo = self.initial_data["permissioninfo"]
        instance.user_permissions.clear()
        permissioninfo = filter(None, str(pinfo).split(','))
        for p in permissioninfo:
            instance.user_permissions.add(Permission.objects.filter(id=int(p)).first())
        obj = super().update(instance, validated_data)
        # 手机号码 需要验证格式并加密存储
        phone = self.initial_data["phone"]
        desc = self.initial_data["desc"]
        models.userInfo.objects.update_or_create(
            defaults={"nickName": instance.get_full_name(), "phone": phone, "email": instance.email, "desc": desc},
            creator=instance.username)
        return obj

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "groups", "user_permissions", "is_staff",
                  "is_active",
                  "is_superuser", "date_joined", "last_login", "extuserinfo"]
        depth = 3


# 系统组菜单管理
class GroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        objGroup = Group.objects.create(**validated_data)
        permissioninfo = filter(None, str(self.initial_data["permissioninfo"]).split(','))
        for p in permissioninfo:
            objGroup.permissions.add(Permission.objects.filter(id=int(p)).first())
        return objGroup

    def update(self, instance, validated_data):
        pinfo = self.initial_data["permissioninfo"]
        instance.permissions.clear()
        permissioninfo = filter(None, str(pinfo).split(','))
        for p in permissioninfo:
            instance.permissions.add(Permission.objects.filter(id=int(p)).first())

        obj = super().update(instance, validated_data)
        return obj

    class Meta:
        model = Group
        fields = '__all__'
        depth = 1


# 系统ContentType管理
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = '__all__'
        depth = 1


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

    def update(self, instance, validated_data):
        print("instance===", instance)
        # 添加权限
        pinfo = self.initial_data["permissioninfo"]
        instance.permission.clear()
        permissioninfo = filter(None, str(pinfo).split(','))
        for p in permissioninfo:
            instance.permission.add(Permission.objects.filter(id=int(p)).first())

        # 添加组
        instance.group.clear()
        ginfo = self.initial_data["groupinfo"]
        groupinfo = filter(None, str(ginfo).split(','))
        for p in groupinfo:
            instance.group.add(Group.objects.filter(id=int(p)).first())
        obj = super().update(instance, validated_data)
        return obj

    class Meta:
        model = models.Menu
        fields = ["id", "title", "url", "sort", "icon", "parent", "parentmenu", "group", "permission", "desc",
                  "creator", "createTime"]
        depth = 1


# 系统权限菜单管理
class PermissionSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        app_label = self.initial_data["app_label"]
        model_name = self.initial_data["model_name"]

        content_type = ContentType.objects.create(app_label=app_label, model=model_name)

        validated_data.update({"content_type_id": content_type.id})
        print(validated_data)
        return Permission.objects.create(**validated_data)

    def update(self, instance, validated_data):
        p_app_label = self.initial_data["app_label"]
        p_model = self.initial_data["model_name"]
        ContentType.objects.update_or_create(defaults={"app_label": p_app_label, "model": p_model},
                                             id=self.initial_data["content_type_id"])
        obj = super().update(instance, validated_data)
        return obj

    class Meta:
        model = Permission
        fields = '__all__'
        depth = 1


# 用户信息实体化

class userInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.userInfo
        fields = ["openid", "creator", "nickName", "sex", "avatar", "phone", "email", "desc", "createTime", "lastTime",
                  "editor"]
