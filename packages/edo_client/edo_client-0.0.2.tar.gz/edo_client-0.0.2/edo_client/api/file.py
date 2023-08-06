# -*- coding: utf-8 -*-
from .base import BaseApi

class FileApi(BaseApi):

    def get(self, path='', uid=''):
        """ 根据路径，或者uid，下载文件, 元数据会在消息头中返回 """
        return self._get('/@@api_get_file', True, uid=uid, path=path)

    def put(self, path, data):
        """ 上传文件 , 返回上传文档元数据"""
        return self._put('%s' % path, False, data=data)

    def metadata(self, path='', uid='', file_limit=10000, list=True):
        """ 查看文件或者文件夹的元数据 """
        return self._get('/@@api_metadata', False, uid=uid, path=path)

