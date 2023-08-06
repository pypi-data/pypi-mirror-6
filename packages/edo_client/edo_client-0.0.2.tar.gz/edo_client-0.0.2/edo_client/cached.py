# -*- encoding:utf-8 -*-
import memcache
from edo_client import OcClient
try:
    from ztq_core import set_key, get_key
except ImportError:
    def set_key(key, value): pass
    def get_key(key): return None

oc_client = None

def init(oc_url, app_id='100000', secret='12345', maxsize=5000, expire=120):
    global oc_client
    oc_client= CachedOcAdminClient(oc_url, app_id, secret, maxsize, expire)


CACHE_PREFIX = "edoaccount"

class CachedOcAdminClient(OcClient):
    """ 支持缓存的admin接口 """

    def __init__(self, server_url, app_id, secret, maxsize=5000, expire=120):
        OcClient.__init__(self, server_url, server_url, app_id, secret)
        self.cache = memcache.lru_cache(maxsize=maxsize, expire=expire)
        self.user_client = OcClient(server_url, server_url, app_id, secret)
        self._token_info_cache = memcache.lru_cache(maxsize=10000, expire=24*3600)
        self.auth_with_rpc(app_id, secret)

    def get_user_token_info(self, token):
        """ 得到用户的token_info """
        try:
            token_info = self._token_info_cache.get(token)
        except KeyError:
            self.user_client.auth_with_token(token)
            token_info = self.user_client.user.get_token_info()
            self._token_info_cache.put(token, token_info)
        return token_info

    def _getValueUseCache(self, cache_key, func, vendor, account, skip_cache=False, **params):
        """ 根据key从redis得到值，否则从rpc调用得到值并放入redis """

        # 从内存中取
        if not skip_cache:
            try:
                return self.cache.get(cache_key)
            except:
                pass

        # 从redis上取
        result = get_key(cache_key)
        if result:
            self.cache.put(cache_key, result)
            return result


        # 从服务器上取 
        result = func(vendor, account, **params)

        if result is None:
            return None

        # 放入redis
        set_key(cache_key, result)

        self.cache.put(cache_key, result)
        return result

    def _getValueUseCache_for_test(self, cache_key, func, skip_cache=False, **params):
        """ 
        仅供测试， 方便了解缓存的使用情况
        
        根据key从redis得到值，否则从rpc调用得到值并放入redis """

        # 从内存中取
        if not skip_cache:
            try:
                print '--BY cache-----' + cache_key + '--------' + str(func)
                return self.cache.get(cache_key)
            except:
                print cache_key, func, 'no this cache'
                pass
        # 从redis上去
        print '--BY redis-----' + cache_key + '--------' + str(func)
        result = get_key(cache_key)
        if result:
            print cache_key, result, 'success'
            self.cache.put(cache_key, result)
            return result

        print '--BY server-----' + cache_key + '--------' + str(func)
        # 从服务器上取 
        result = func(**params)
        print cache_key, result, 'success'

        if result is None:
            return None
        # 放入redis
        set_key(cache_key, result)

        self.cache.put(cache_key, result)
        return result

    def getPrincipalInfo(self, vendor, account,  pid,  skip_cache=False):
        """ 得到人员和组基本信息
        人员: id，title，mobile，email
        组:  id,title
        """
        # 从缓存中读取帐户信息，
        # 如果没有，则想服务器发起xmlrpc请求
        if pid == 'groups.role.AccountAdmin':
            return {'title':'系统管理人'}
        elif pid == 'zope.Authenticated':
            return {'title':'任意登录用户'}
        elif pid == 'zope.Everybody':
            return {'title':'全部人'}
        elif pid == 'zope.anybody':
            return {'title':'任何人'}
        # 内存缓存
        key = "pinfo:%s.%s.%s:%s"%(CACHE_PREFIX, vendor, account, pid)

        value = self._getValueUseCache(key, self.admin.principal_info, vendor, account, skip_cache=skip_cache, user_id=pid) 
        if not value:
            return {'id':pid, 'title':pid, 'mobile':'', 'email':''}
        return value

    def listPrincipalInfo(self, vendor, account, pids, skip_cache=False):
        """ 批量得到人员和组的信息 """
        values = []
        users = []

        for pid in pids:
            if pid == 'groups.role.AccountAdmin':
                values.append({'title':'系统管理人'})
            elif pid == 'zope.Authenticated':
                values.append({'title':'任意登录用户'})
            elif pid == 'zope.Everybody':
                values.append({'title':'全部人'})
            elif pid == 'zope.anybody':
                values.append({'title':'任何人'})
            else:
                if skip_cache:
                    users.append(pid)
                    continue

                key = "pinfo:%s.%s.%s:%s"%(CACHE_PREFIX, vendor, account, pid)
                value = None
                try:
                    value = self.cache.get(key)
                except KeyError:
                    value = None

                if value is None:
                    users.append(pid)
                else:
                    values.append(value)

        if len(users) == 1:
            value = self.getPrincipalInfo(vendor, account, users[0], skip_cache=True)
            values.append(value)

        elif len(users) > 1:
            infos = self.admin.list_principal_info(vendor=vendor, account=account, users=users)
            values.extend(infos)
            for info in infos:
                key = "pinfo:%s.%s.%s:%s"%(CACHE_PREFIX, vendor, account, info['id'])
                self.cache.put(key, info)
                set_key(key, info)

        return values

    def listUserGroups(self, vendor, account, user_id):
        key = "gusers:%s.%s.%s:%s"%(CACHE_PREFIX, vendor, account, user_id)
        remote_groups= self._getValueUseCache(key, self.admin.list_user_groups, vendor=vendor, account=account, key=user_id) or {}
        return remote_groups

    def listFlatUserGroups(self, vendor, account, user_id):
        groups = []
        groupinfo = self.listUserGroups(vendor, account, user_id)
        for value in groupinfo.values():
            groups.extend(value)
        return groups

    def listGroupMembers(self, vendor, account, group_id):
        key = "gmembers:%s.%s.%s:%s"%(CACHE_PREFIX, vendor, account, group_id)
        return self._getValueUseCache(key, self.admin.list_group_members, vendor=vendor, account=account, key=group_id) or []

    def listOrgStructure(self, vendor, account):
        key = "orgstr:%s.%s.%s" % (CACHE_PREFIX, vendor, account)

        org_structure = self._getValueUseCache(key, self.admin.list_org_structure, vendor=vendor, account=account) or {}
        return org_structure

    def listCompanies(self, vendor, account):
        key = "companies:%s.%s.%s" % (CACHE_PREFIX, vendor, account)
        return self._getValueUseCache(key, self.admin.list_companies, vendor=vendor, account=account) or []

    def lookupReviewer(self, vendor, account, user_id, reviewer_table, step):
        """ 通过字典查找审核人

        reviwer_table应该是一个三列的动态表格：

        - step: (步骤，可选，限制某个步骤，单行文本),
        - comment(说明，单行文本),
        - reviewer（审核人，人员选择，）
        - members（审核人，人员选择，可选择人和组）

        用户id优先级，高于组id优先级，先找用户id, 找不到再找组id
        """
        if isinstance(user_id, list):
            user_id = user_id[0]

        for row in reviewer_table:
            members = row.get('members', ['groups.tree.default'])
            row_step = row.get('step', step)  # 和从前的兼容
            if user_id in members and row_step == step:
                return row['reviewer']

        user_groups = set(self.listFlatUserGroups(vendor, account, user_id))
        for row in reviewer_table:
            members = row.get('members', ['groups.tree.default'])
            row_step = row.get('step', step)  # 和从前的兼容
            if len(user_groups.intersection(members)) > 0 and row_step == step:
                return row['reviewer']

    def listInstances(self, vendor,  account, skip_cache=False):
        key = "instanceinfo:%s:%s" % (vendor, account)
        value = self._getValueUseCache(key, self.admin.list_instances, vendor, account, skip_cache=skip_cache)
        return value

    def getOUDetail(self, vendor, account, ou_id, include_disabled=False, skip_cache=False):
        key = "oudetail:%s.%s.%s:%s:%s"%(CACHE_PREFIX, vendor, account, ou_id, include_disabled)
        value = self._getValueUseCache(key, self.admin.ou_detail, vendor=vendor, account=account, ou_id=ou_id, include_disabled=include_disabled, skip_cache=skip_cache) or {}
        return value


