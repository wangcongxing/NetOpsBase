from django.test import TestCase
import requests

# Create your tests here.
import requests

import requests, json
import ast

print(ast.literal_eval("{'http': None,'https': None,}"))




menu = [{"name": "home", 'title': '主页', 'icon': 'layui-icon-home',
         'list': [{'name': 'console', 'title': '控制台', 'jump': '/'},
                  {'name': 'homepage1', 'title': '主页一', 'jump': 'home/homepage1'},
                  {'name': 'homepage2', 'title': '主页二', 'jump': 'home/homepage2'}]},
        {'name': 'component', 'title': '配置管理', 'icon': 'layui-icon-component', 'list': []},
        {'name': 'netcheck', 'title': '网络审计', 'icon': 'layui-icon-auz', 'list': []},
        {'name': 'template', 'title': '网络探测', 'icon': 'layui-icon-template', 'list': []},
        {'name': 'app', 'title': '资产管理', 'icon': 'layui-icon-app', 'list': []},
        {'name': 'busMan', 'title': '业务管理', 'icon': 'layui-icon-template-1', 'list': []},
        {'name': 'task', 'title': '任务编排', 'icon': 'layui-icon-read', 'list': []},
        {'name': 'loginfo', 'title': '报警信息', 'icon': 'layui-icon-fire', 'list': []},
        {'name': 'user', 'title': '用户', 'icon': 'layui-icon-user',
         'list': [{'name': 'user', 'title': '网站用户', 'jump': 'user/user/list'},
                  {'name': 'administrators-list', 'title': '后台管理员', 'jump': 'user/administrators/list'},
                  {'name': 'administrators-rule', 'title': '角色管理', 'jump': 'user/administrators/role'}]},
        {'name': 'set', 'title': '设置', 'icon': 'layui-icon-set', 'list': [
            {'name': 'system', 'title': '系统设置', 'spread': True,
             'list': [{'name': 'website', 'title': '网站设置', 'jump': '/set/system/website'},
                      {'name': 'menus', 'title': '菜单管理', 'jump': 'set/menus/menulist'},
                      {'name': 'taskwork', 'title': '定时任务', 'jump': 'set/taskwork/tasklist'}]},
            {'name': 'auth', 'title': '权限设置', 'spread': True,
             'list': [{'name': 'permissionGroup', 'title': '权限', 'jump': 'set/auth/permission'},
                      {'name': 'permissionGroup', 'title': '权限组', 'jump': 'set/auth/group'}]},
            {'name': 'user', 'title': '我的设置', 'spread': True,
             'list': [{'name': 'info', 'title': '基本资料', 'jump': '/set/user/info'},
                      {'name': 'password', 'title': '修改密码', 'jump': '/set/user/password'}]}]},
        {'name': 'get', 'title': '关于', 'icon': 'layui-icon-auz', 'jump': 'system/about'}]

for pitem in menu:
    pname = pitem["name"]
    ptitle = pitem["title"]
    picon = pitem["icon"]
    plist = pitem["list"] if "list" in pitem.keys() else []
    for citem in plist:
        cname = citem["name"]
        ctitle = citem["title"]
        cjump = citem["jump"] if "jump" in citem.keys() else ""
        cclist = citem["list"] if "list" in citem.keys() else []
        for ccitem in cclist:
            ccname = ccitem["name"]
            cctitle = ccitem["title"]
            ccjump = ccitem["jump"]
