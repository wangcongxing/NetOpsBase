import pymysql
pymysql.version_info = (1, 4, 0, "final", 0)
pymysql.install_as_MySQLdb()
from celery_tasks.celeryapp import app as celery_app
__all__ = ('celery_app',)
