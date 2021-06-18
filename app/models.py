from django.db import models
from django.contrib.auth.models import User, Group, Permission
from mptt.models import MPTTModel
import datetime, uuid, os

from django_celery_beat.models import PeriodicTask, IntervalSchedule


# 自动生成guid
def newuuid():
    return str(uuid.uuid4())


# 提取出公共的方法evaluation_directory_path获取图片后缀
# 使用uuid创建唯一的图片名，并保存的路径和文件名一并返回
def evaluation_directory_path(item_id, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join("avatar", filename)


# Create your models here.
class Menu(MPTTModel):
    """
    一级菜单表
    """
    title = models.CharField(verbose_name='菜单名称', max_length=255, default="", null=True,
                             blank=True, )
    name = models.CharField(verbose_name='菜单别名', max_length=255, default=newuuid, null=True,
                            blank=True, )  # unique唯一
    url = models.CharField(verbose_name='含正则的URL', max_length=128, default="", null=True,
                           blank=True, )
    # 图标http://fontawesome.dashgame.com/
    sort = models.IntegerField(verbose_name='显示顺序', default=1)
    icon = models.CharField(verbose_name='菜单图标', max_length=32, blank=True)  # blank 为admin后台可以空
    parent = models.ForeignKey('self', verbose_name='所属一级菜单', help_text='null表示不是菜单，否则为二级菜单', null=True, blank=True,
                               related_name='children', on_delete=models.CASCADE)
    group = models.ManyToManyField(Group, verbose_name='组', blank=True)
    desc = models.TextField(verbose_name='描述', max_length=50000, blank=True, default="")
    permission = models.ManyToManyField(Permission, verbose_name='用户权限', blank=True)
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="创建者",
                                related_name="menu_creator")
    editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="修改者",
                               related_name="menu_editor")

    def __str__(self):  # 循环查找父菜单返回字符串 self-parent-parent
        return self.title

    class MPTTMeta:
        parent_attr = 'parent'

    class Meta:
        verbose_name = verbose_name_plural = '菜单表'


# 调度任务扩展表 可支持动态配置url执行定时任务

class celeryExtend(models.Model):
    periodictask = models.ForeignKey(PeriodicTask, verbose_name='周期性任务', help_text='celery-PeriodicTask', null=True,
                                     blank=True,
                                     on_delete=models.CASCADE)
    tasktype = models.CharField(verbose_name='任务类型', max_length=255, default="", null=True,
                                blank=True, )
    nid = models.CharField(max_length=255, verbose_name="任务id", blank=False, null=False, default=newuuid)
    url = models.URLField(verbose_name='URL地址', max_length=255, default="", null=True,
                          blank=True, )
    reqmethod = models.CharField(verbose_name='请求方式', max_length=255, default="", null=True,
                                 blank=True, )
    reqheaders = models.TextField(verbose_name='请求头', max_length=50000, default="", null=True,
                                  blank=True, )
    proxies = models.TextField(verbose_name='请求代理', max_length=50000, default="{'http': None,'https': None,}",
                               null=True,
                               blank=True, )
    payload = models.TextField(verbose_name='请求体', max_length=50000, default="", null=True,
                               blank=True, )
    phone = models.CharField(verbose_name='手机号码', max_length=255, default="", null=True,
                             blank=True, )
    email = models.CharField(verbose_name='邮箱', max_length=255, default="", null=True,
                             blank=True, )
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="创建者",
                                related_name="celeryExtend_creator")
    editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="修改者",
                               related_name="celeryExtend_editor")

    class Meta:
        verbose_name = verbose_name_plural = '用于支持定时调用URL任务'


# 网站设置
class webSiteSet(models.Model):
    webName = models.CharField(verbose_name='网站名称', max_length=255, default="", null=True, blank=True, )
    webUrl = models.URLField(verbose_name='网站域名', max_length=255, default="", null=True, blank=True, )
    cacheTime = models.IntegerField(verbose_name='缓存时间', default="10", null=True, blank=True, )
    uploadFileSize = models.IntegerField(verbose_name='最大文件上传', default="1024", null=True, blank=True, )
    fileExt = models.CharField(verbose_name='上传文件类型', max_length=255, default="", null=True, blank=True, )
    homeTitle = models.CharField(verbose_name='首页标题', max_length=255, default="", null=True, blank=True, )
    META = models.TextField(verbose_name='META关键词', default="", null=True, blank=True, )
    METADESC = models.TextField(verbose_name='META描述', default="", null=True, blank=True, )
    license = models.TextField(verbose_name='版权信息', default="", null=True, blank=True, )
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="创建者",
                                related_name="webSiteSet_creator")
    editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="修改者",
                               related_name="webSiteSet_editor")

    class Meta:
        verbose_name = verbose_name_plural = '网站设置'


# 基本资料
class userInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户", null=True, blank=True, )
    openid = models.CharField(verbose_name='openid', max_length=255, default="", null=True, blank=True, )
    nickName = models.CharField(verbose_name='姓名', max_length=255, default="", null=True, blank=True, )
    sex = models.CharField(verbose_name='性别', max_length=255, default="", null=True, blank=True, )
    avatar = models.ImageField(verbose_name='头像', max_length=255, default="", null=True, blank=True,
                               upload_to=evaluation_directory_path)
    phone = models.CharField(verbose_name='手机', max_length=255, default="", null=True, blank=True, )
    email = models.CharField(verbose_name='邮箱', max_length=255, default="", null=True, blank=True, )
    desc = models.TextField(verbose_name='备注', default="", null=True, blank=True, )
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="创建者",
                                related_name="userInfo_creator")
    editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="修改者",
                               related_name="userInfo_editor")

    class Meta:
        verbose_name = verbose_name_plural = '用户信息'


# 权限组信息
class groupInfo(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, verbose_name="权限组")
    permission = models.ManyToManyField(Permission, verbose_name='权限', blank=True)
    desc = models.TextField(verbose_name='描述', default="", null=True, blank=True, )
    createTime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    lastTime = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    creator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="创建者",
                                related_name="groupInfo_creator")
    editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="修改者",
                               related_name="groupInfo_editor")

    # 拥有的权限
    def get_permission(self):
        pass

    class Meta:
        verbose_name = verbose_name_plural = '权限组信息'
