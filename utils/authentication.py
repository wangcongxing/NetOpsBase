from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework_jwt.settings import api_settings
from utils.APIResponseResult import get_parameter_dic

class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        request.data.update(request.query_params.dict())
        dataDict = get_parameter_dic(request)
        print("request.data==================", request.data)
        if 'access_token' in dataDict:
            try:
                token = dataDict['access_token']
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                user_dict = jwt_decode_handler(token)
                print("user_dict==>",user_dict)
                return (user_dict, token)
            except Exception as ex:
                raise exceptions.AuthenticationFailed(detail={'code': 401, 'msg': 'access_token已过期'})
        else:
            raise exceptions.AuthenticationFailed(detail={'code': 400, 'msg': '缺少access_token'})

    def authenticate_header(self, request):
        pass
