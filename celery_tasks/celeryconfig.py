from django.conf import settings
import os

# 为celery设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'NetOpsBase.settings')

# 设置结果存储
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/9'
# 设置代理人broker
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/8'
# celery 的启动工作数量设置
CELERY_WORKER_CONCURRENCY = 20
# 任务预取功能，就是每个工作的进程／线程在获取任务的时候，会尽量多拿 n 个，以保证获取的通讯成本可以压缩。
CELERY_PREFETCH_MULTIPLIER = 20
# 非常重要,有些情况下可以防止死锁
CELERY_FORCE_EXECV = True
# celery 的 worker 执行多少个任务后进行重启操作
# CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
# 禁用所有速度限制，如果网络资源有限，不建议开足马力。
CELERY_DISABLE_RATE_LIMITS = True

# celery beat配置

CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = settings.TIME_ZONE
CELERY_DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'