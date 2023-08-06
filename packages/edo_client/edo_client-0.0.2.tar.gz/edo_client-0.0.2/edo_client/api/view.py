# -*- coding: utf-8 -*-
from .base import BaseApi

class Viewer(BaseApi):
    def get_account_security(self, account, vendor):
        return self._get('/get_account_security', account=account,  vendor=vendor)


