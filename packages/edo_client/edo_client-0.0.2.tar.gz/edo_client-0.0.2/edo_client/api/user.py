# -*- coding: utf-8 -*-
from .base import BaseApi

class UserApi(BaseApi):

    def get_token_info(self):
        """ 当前用户的账户信息 """
        return self._get('/api_get_token_info', False)

    def check_password(self, password):
        return self._get('/api_check_password', False, password=password)

    def reset_password(self, password, new_password):
        return self._get('/api_reset_password', False, password=password, new_password=new_password)

    def enable_dynamic_auth(self, key, code):
        return self._get('/api_enable_dynamic_auth', False, key=key, code=code)

    def disable_dynamic_auth(self, code):
        return self._get('/api_disable_dynamic_auth', False, code=code)

    def is_dynamic_auth_enabled(self):
        return self._get('/api_is_dynamic_auth_enabled', False)
