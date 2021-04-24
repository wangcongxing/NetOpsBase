from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, data_status=0, data_msg='ok', results=None
                 , http_status=None, headers=None, exception=False, **kwargs):
        # data的初始状态：状态码与状态信息
        data = {
            'code': data_status,
            'msg': data_msg,
        }
        # data的响应数据体
        # results可能是False、0等数据，这些数据某些情况下也会作为合法数据返回
        if results is not None:
            data['data'] = results
        # data响应的其他内容
        # if kwargs is not None:
        #     for k, v in kwargs:
        #         setattr(data, k, v)
        data.update(kwargs)

        # 重写父类的Response的__init__方法
        super().__init__(data=data, status=http_status, headers=headers, exception=exception)

'''
编写参数统一处理的方法
总结一下, 当url有?param=1&param=2这样的参数时忽略body中的参数, 例如get,delete提交,如果query_params有内容, 则忽略body内容. 将QueryDict转为dict返回, 再判断request.data中是否有内容, 类型如何.

'''
from django.http import QueryDict
from rest_framework.request import Request
def get_parameter_dic(request, *args, **kwargs):
    if isinstance(request, Request) == False:
        return {}

    query_params = request.query_params
    if isinstance(query_params, QueryDict):
        query_params = query_params.dict()
    result_data = request.data
    if isinstance(result_data, QueryDict):
        result_data = result_data.dict()

    if query_params != {}:
        return query_params
    else:
        return result_data