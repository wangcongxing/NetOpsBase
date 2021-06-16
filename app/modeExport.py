# https://pypi.org/project/drf-renderer-xlsx/
# 为了避免流传输的文件没有文件名(浏览器通常将其默认为没有扩展名的 download)
# 需要使用 mixin 覆盖 Content-Disposition标头
# 如果未提供文件名则默认为 data.xlsx。
from app import models, modelSerializers
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
import os, uuid, time
from django_celery_beat.models import PeriodicTask, IntervalSchedule


# 导出任务信息
class periodicTaskExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = PeriodicTask.objects.all().order_by('-id')
    serializer_class = modelSerializers.PeriodicTaskExportSerializer
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "ID",
            "任务名称",
            "执行函数",
            "参数",
            "扩展参数",
            "队列",
            "exchange",
            "routing_key",
            "headers",
            "优先权",
            "过期时间",
            "过期秒数",
            "运行一次",
            "启动时间",
            "是否禁用",
            "最后一次运行时间",
            "运行次数",
            "修改时间",
            "描述",
            "频率",
            "solar",
            "crontab",
            "测定时间"
        ],
        'column_width': [5, 30, 30, 40, 40, 40, 50, 50, 50, 55, 55, 30, 30, 40, 40, 40, 50, 50, 50, 55, 20, 55, 50],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }




# 导出用户信息
class userInfoExport(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = models.userInfo.objects.all().order_by('-id')
    serializer_class = modelSerializers.userInfoSerializer
    renderer_classes = (XLSXRenderer,)
    filename = '{}.xlsx'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    column_header = {
        'titles': [
            "openid",
            "账号",
            "姓名",
            "性别",
            "头像",
            "手机",
            "邮箱",
            "备注",
            "创建时间",
            "修改时间",
            "创建者",
            "修改者"
        ],
        'column_width': [30, 30, 30, 40, 40, 40, 50, 50, 50, 55, 55, ],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }
    body = {
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': False,
                'color': 'FF000000',
            }
        },
        'height': 40,
    }
