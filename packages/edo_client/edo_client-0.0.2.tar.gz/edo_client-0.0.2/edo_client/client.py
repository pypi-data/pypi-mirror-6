# -*- coding: utf-8 -*-
from pyoauth2 import AccessToken
from patch import Client
from edo_client.api import OcApi, WoApi, ViewerApi
from error import ApiError
import md5

class BaseClient(WoApi):
    """ token管理"""

    def __init__(self, auth_host, api_host, key, secret, redirect='', refresh_hook=None):
        self.auth_host = auth_host
        self.api_host = api_host
        self.redirect_uri = redirect
        self.refresh_hook = refresh_hook
        self.client = Client(key, secret,
                       site=api_host, 
                       authorize_url= self.auth_host+ '/@@authorize', 
                       token_url= self.auth_host + '/@@access_token')

        self.access_token = None
        self.sites = []

    @property
    def token_code(self):
        return getattr(self.access_token, 'token', None)

    @property
    def refresh_token_code(self):
        return getattr(self.access_token, 'refresh_token', None)

    def refresh_token(self, refresh_token):
        access_token = AccessToken(self.client, token='', refresh_token=refresh_token)
        self.access_token = access_token.refresh()
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

    @property
    def authorize_url(self):
        return self.client.auth_code.authorize_url(redirect_uri=self.redirect_uri)

    def auth_with_code(self, code, account='zopen', return_token_info=False):
        self.access_token, token_info = self.client.auth_code.get_token(code, account=account, return_token_info=return_token_info, redirect_uri=self.redirect_uri)
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

        return token_info

    def auth_with_password(self, username, password, account, **opt):
        self.access_token = self.client.password.get_token(username=username,
                                 password=password, account=account, redirect_uri=self.redirect_uri, **opt)
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

    def auth_with_borrow_token(self, access_token, **opt):
        self.access_token = self.client.borrow.get_token(access_token=access_token, **opt)
        if not self.token_code:
            raise ApiError(403 ,403, 'Authentication failed')

    def auth_with_token(self, token, refresh_token=''):
        self.access_token = AccessToken(self.client, token=token, refresh_token=refresh_token)

    def auth_with_rpc(self, app_id, secret):
        token = md5.new(app_id + secret).hexdigest()
        self.auth_with_token(token)

class OcClient(BaseClient, OcApi):
    """ 提供多种token获取途径"""

    def get_wo_client(self, instance_name='default'):
        sites = self.account.list_instances()
        client = WoClient(self.auth_host, sites[instance_name]['url'], self.client.id, 
                        self.client.secret, self.redirect_uri, self.refresh_hook)
        client.auth_with_token(self.token_code)
        return client

class WoClient(BaseClient, WoApi):
    pass

class ViewerClient(BaseClient, ViewerApi):
    pass

if __name__ == '__main__':
    pass

