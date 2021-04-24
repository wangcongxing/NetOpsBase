from rest_framework.throttling import SimpleRateThrottle


class AnonRateThrottle(SimpleRateThrottle):
    """
    匿名用户，根据IP进行限制
    """
    scope = "so_anon"

    def get_cache_key(self, request, view):
        # 用户已登录，则跳过 匿名频率限制
        if request.user:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class UserRateThrottle(SimpleRateThrottle):
    """
    登录用户，根据用户token限制
    """
    scope = "so_user"

    def get_ident(self, request):
        """
        认证成功时：request.user是用户对象；request.auth是token对象
        :param request:
        :return:
        """
        # return request.auth.token
        return "user_token"

    def get_cache_key(self, request, view):
        """
        获取缓存key
        :param request:
        :param view:
        :return:
        """
        # 未登录用户，则跳过 Token限制
        if not request.user:
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }