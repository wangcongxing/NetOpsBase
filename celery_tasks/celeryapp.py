from celery import Celery
from celery_tasks import celeryconfig
from django.utils import timezone

# 创建celery app
app = Celery("tasks")

# 从单独的配置模块中加载配置
app.config_from_object(celeryconfig, namespace="CELERY")

# 设置app自动加载任务
app.autodiscover_tasks(['celery_tasks'])

# 解决时区问题，定时任务启动就循环输出
# app.now = timezone.now