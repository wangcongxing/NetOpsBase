from django.db import models
from django.contrib.auth.models import User, Group, Permission
from mptt.models import MPTTModel
import datetime


# Create your models here.
class Menu(MPTTModel):
    """
    一级菜单表
    """
    title = models.CharField(verbose_name='菜单名称', max_length=32)
    name = models.CharField(verbose_name='URL别名', max_length=255, unique=True, default="", null=True,
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

    creator = models.CharField(max_length=255, verbose_name="创建者", blank=True, null=True, default="")
    editor = models.CharField(max_length=255, verbose_name="修改者", blank=True, null=True, default="")

    def __str__(self):  # 循环查找父菜单返回字符串 self-parent-parent
        return self.title

    class MPTTMeta:
        parent_attr = 'parent'

    class Meta:
        verbose_name = verbose_name_plural = '菜单表'
