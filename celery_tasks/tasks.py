from celery import shared_task

# 启动
# 参考资料
# https://www.jianshu.com/p/15e02fea4263
# https://github.com/hongjinquan/django-schedule-celery
# https://www.shuzhiduo.com/A/8Bz8woOxdx/
# celery -A NetOpsBase beat --loglevel=info -f logs/celerybeat_out.log --scheduler django_celery_beat.schedulers:DatabaseScheduler
# celery -A NetOpsBase beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler -f logs/celerybeat_out.log

# celery -A NetOpsBase worker -l info # 不带日志启动
# celery -A NetOpsBase worker --pool=solo -l info -f logs/celery.log # 带日志启动
# 修改tasks 类必须重启 否则无法生效滴
from celery_tasks.celeryapp import app
import time
import requests, json
from app import models as appModel
import ast


# 创建任务函数
@app.task
def my_task1(a, b, c):
    print("任务1函数正在执行....")
    print("任务1函数休眠10秒...")
    # time.sleep(10)
    return a + b + c


@app.task
def my_task2():
    print("任务2函数正在执行....")
    print("任务2函数休眠10秒....")


@app.task
def sendUrl(nid):
    print("nid=", nid)

    celeryextend = appModel.celeryExtend.objects.filter(id=nid).first()
    if celeryextend is None:
        return "nid={},未找到需要请求的url,请求失败...".format(nid)

    response = requests.request(celeryextend.reqmethod, celeryextend.url, headers=ast.literal_eval(celeryextend.reqheaders),
                                proxies=ast.literal_eval(celeryextend.proxies),
                                data=ast.literal_eval(celeryextend.payload))
    print(response.text)
    return response.text  # response.text
