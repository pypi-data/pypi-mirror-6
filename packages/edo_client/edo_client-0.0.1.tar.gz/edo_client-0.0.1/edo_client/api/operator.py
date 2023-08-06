# -*- coding: utf-8 -*-
from .base import BaseApi

class OperatorAPI(BaseApi):

    def createoperationinstance(self, **params):
        return self._get('/@@api_createoperationinstance', False, **params)

    def updateoperationoptions(self, **params):
        return self._get('/@@api_updateoperationoptions', False, **params)

    def listoperationoptions(self, **params):
        return self._get('/@@api_listoperationoptions', False, **params)

    def checkcurrentoptions(self, **params):
        return self._get('/@@api_checkcurrentoptions', False, **params)

    def destroyoperationinstance(self, **params):
        return self._get('/@@api_destroyoperationinstance', False, **params)

    def setup(self, **params):
        return self._get('/@@api_setup', False, **params)

    def getLicense(self, **params):
        return self._get('/@@api_getLicense', False, **params)

    def updateLicense(self, **params):
        return self._get('/@@api_updateLicense', False, **params)


