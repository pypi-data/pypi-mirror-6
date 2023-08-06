# -*- coding: utf-8 -*-
from edo_client.error import ApiError

DEFAULT_START = 0
DEFAULT_COUNT = 20

def check_execption(func):
    def _check(*arg, **kws):
        # 网络错误, 连接不到服务器
        try:
            resp = func(*arg, **kws)
        except:
            raise ApiError(111, 111, 'network error')

        # 地址错误
        if resp.status == 404:
            raise ApiError(404, 404, '404 Not Found')

        if resp.status > 500:
            raise ApiError(500, 500, '500 Server Error!')

        response = resp.resp
        if resp.status >= 400:
            self = arg[0]
            result = response.json()
            if result['code'] == 401 and  self.refresh_hook:
                self.client.refresh_token(self.access_token.refresh_token)
                if self.refresh_hook:
                    self.refresh_hook(self.access_token.token, self.access_token.refresh_token)
                return _check(*arg, **kws)

            raise ApiError(resp.status, result['code'], result['message'])

        # 是否返回json格式的数据
        raw = arg[2]
        if raw:
            return response.raw
        else:
            return response.json()

    return _check


class BaseApi(object):
    def __init__(self, client, access_token, refresh_hook):
        self.client = client
        self.refresh_hook = refresh_hook
        self.access_token = access_token

    def __repr__(self):
        return '<EverydoAPI Base>'

    @check_execption
    def _get(self, url, raw, **opts):
        return self.access_token.get(url, **opts)

    @check_execption
    def _post(self, url, raw, **opts):
        return self.access_token.post(url, **opts)

    @check_execption
    def _put(self, url, raw, **opts):
        return self.access_token.put(url, **opts)

    @check_execption
    def _patch(self, url, raw, **opts):
        return self.access_token.patch(url, **opts)

    @check_execption
    def _delete(self, url, raw, **opts):
        return self.access_token.delete(url, **opts)
 
