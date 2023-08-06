# -*- coding: utf-8 -*-
from .base import BaseApi

class OrgAPI(BaseApi):

    # FIXME vendor作为第一个参数，调用的地方，需要传递具体的vendor
    def remove_user(self, account, key, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_remove_user' % (vendor, account), False, key=key)

    def principal_info(self, account, user_id, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_get_principal_info' % (vendor, account), False,  user_id=user_id)

    def has_user(self, account, username, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_has_user' % account, False, username=username)

    def list_user_groups(self, account, key, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_list_user_groups' % (vendor, account), False, key=key)

    def list_principal_info(self, account, users, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_list_principal_info' % account, False, users=users)

    def sync(self, account, ous, groups, users, send_mail, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_sync' % account, False, ous=str(ous), groups=str(groups), users=str(users), send_mail=send_mail)

    def remove_ous(self, account, key, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_remove_ous' % account, False, key=key)
    
    def has_ou(self, account, ou_id, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_has_ou' % account, False, ou_id=ou_id)

    def list_group_members(self, account, key, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_list_group_members' % account, False, key=key)

    def list_org_structure(self, account, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_list_org_structure' % account, False,)

    def list_companies(self, account, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_list_companies' % account, False)

    def remove_groups(self, account, key, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_remove_groups' % account, False, key=key)

    def ou_detail(self, account, ou_id, include_disabled, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_get_ou_detail' % account, False, ou_id=ou_id, include_disabled=include_disabled)

    def add_group_users(self, account, group_id, user_ids, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_add_group_users' % account, False, group_id=group_id, user_ids=user_ids)

    def remove_group_users(self, account, group_id, user_ids, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_remove_group_users' % account, False, group_id=group_id, user_ids=user_ids)

    def set_ldap_config(self, account, server_address, enable, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_set_ldap_config' % account, False, server_address=server_address, enable=enable)

    def get_ldap_config(self, account, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_get_ldap_config' % account, False)

    def set_allowed_services(self, account, username, app_name, instance_name, services, vendor='standalone'):
        if not isinstance(services, (list, tuple, set)): services = (services, )
        return self._get('/vendors/%s/accounts/%s/api_set_allowed_services' % account, False, username=username, instance_name=instance_name, services=services, app_name=app_name)

    def get_allowed_services(self, account, username, app_name, instance_name, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_get_allowed_services' % account, False, username=username, instance_name=instance_name, app_name=app_name)

    def list_instances(self, account, vendor='standalone'):
        return self._get('/vendors/%s/accounts/%s/api_list_instances' % (vendor, account), False)


