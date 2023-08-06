# -*- coding: utf-8 -*-
from .file import FileApi
from .user import UserApi
from .admin import OrgAPI
from .view import Viewer
from operator import OperatorAPI

class OcApi(object):

    @property
    def user(self):
        """ 当前用户相关的接口 """
        return UserApi(self, self.access_token, self.refresh_hook)

    @property
    def admin(self):
        """ 组织架构相关的管理接口"""
        return OrgAPI(self, self.access_token, self.refresh_hook)

class WoApi(object):

    @property
    def files(self):
        return FileApi(self, self.access_token, self.refresh_hook)

    @property
    def operator(self):
        return OperatorAPI(self, self.access_token, self.refresh_hook)

    @property
    def workflows(self):
        return WorkflowApi(self, self.access_token, self.refresh_hook)

class ViewerApi(object):

    @property
    def account(self):
        return Viewer(self, self.access_token, self.refresh_hook)
        

