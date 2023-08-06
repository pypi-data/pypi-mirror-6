# -*- coding: utf-8 -*-
from .base import BaseApi

class OrgAPI(BaseApi):

    def remove_user(self, vendor, account, key):
        return self._get('/vendors/%s/accounts/%s/api_remove_user' % (vendor, account), False, key=key)

    def principal_info(self, vendor, account, user_id):
        return self._get('/vendors/%s/accounts/%s/api_get_principal_info' % (vendor, account), False,  user_id=user_id)

    def has_user(self, vendor, account, username):
        return self._get('/vendors/%s/accounts/%s/api_has_user' % (vendor, account), False, username=username)

    def list_user_groups(self, vendor, account, key):
        return self._get('/vendors/%s/accounts/%s/api_list_user_groups' % (vendor, account), False, key=key)

    def list_principal_info(self, vendor, account, users):
        return self._get('/vendors/%s/accounts/%s/api_list_principal_info' % (vendor, account), False, users=users)

    def sync(self, vendor, account, ous, groups, users, send_mail):
        return self._get('/vendors/%s/accounts/%s/api_sync' % (vendor, account), False, ous=str(ous), groups=str(groups), users=str(users), send_mail=send_mail)

    def remove_ous(self, vendor, account, key):
        return self._get('/vendors/%s/accounts/%s/api_remove_ous' % (vendor, account), False, key=key)
    
    def has_ou(self, vendor, account, ou_id):
        return self._get('/vendors/%s/accounts/%s/api_has_ou' % (vendor, account), False, ou_id=ou_id)

    def list_group_members(self, vendor, account, key):
        return self._get('/vendors/%s/accounts/%s/api_list_group_members' % (vendor, account), False, key=key)

    def list_org_structure(self, vendor, account):
        return self._get('/vendors/%s/accounts/%s/api_list_org_structure' % (vendor, account), False,)

    def list_companies(self, vendor, account):
        return self._get('/vendors/%s/accounts/%s/api_list_companies' % (vendor, account), False)

    def remove_groups(self, vendor, account, key):
        return self._get('/vendors/%s/accounts/%s/api_remove_groups' % (vendor, account), False, key=key)

    def ou_detail(self, vendor, account, ou_id, include_disabled):
        return self._get('/vendors/%s/accounts/%s/api_get_ou_detail' % (vendor, account), False, ou_id=ou_id, include_disabled=include_disabled)

    def add_group_users(self, vendor, account, group_id, user_ids):
        return self._get('/vendors/%s/accounts/%s/api_add_group_users' % (vendor, account), False, group_id=group_id, user_ids=user_ids)

    def remove_group_users(self, vendor, account, group_id, user_ids):
        return self._get('/vendors/%s/accounts/%s/api_remove_group_users' % (vendor, account), False, group_id=group_id, user_ids=user_ids)

    def set_ldap_config(self, vendor, account, server_address, enable):
        return self._get('/vendors/%s/accounts/%s/api_set_ldap_config' % (vendor, account), False, server_address=server_address, enable=enable)

    def get_ldap_config(self, vendor, account):
        return self._get('/vendors/%s/accounts/%s/api_get_ldap_config' % (vendor, account), False)

    def set_allowed_services(self, vendor, account, username, app_name, instance_name, services):
        if not isinstance(services, (list, tuple, set)): services = (services, )
        return self._get('/vendors/%s/accounts/%s/api_set_allowed_services' % (vendor, account), False, username=username, instance_name=instance_name, services=services, app_name=app_name)

    def get_allowed_services(self, vendor, account, username, app_name, instance_name):
        return self._get('/vendors/%s/accounts/%s/api_get_allowed_services' % (vendor, account), False, username=username, instance_name=instance_name, app_name=app_name)

    def list_instances(self, vendor, account):
        return self._get('/vendors/%s/accounts/%s/api_list_instances' % (vendor, account), False)


