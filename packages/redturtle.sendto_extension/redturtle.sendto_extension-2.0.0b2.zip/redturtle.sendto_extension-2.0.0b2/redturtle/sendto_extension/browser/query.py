# -*- coding: utf-8 -*-

import json
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class QuerySiteMemberView(BrowserView):
    """Query for esistings site members"""
    
    def __call__(self, *args, **kwargs):
        term = self.request.form.get('term', '')
        response = self.request.response
        
        acl_users = getToolByName(self.context, 'acl_users')
        
        results = list(acl_users.searchUsers(name=term))
        results += [x for x in acl_users.searchUsers(fullname=term) if x not in results]
        results += [x for x in acl_users.searchUsers(email=term) if x not in results]
        results = sorted(results, key=lambda m: m.get('fullname') or m.get('login'))
        
        json_results = []
        
        for member_data in results:
            if member_data.get('email'):
                json_results.append({'value': member_data.get('login'),
                                     'label': member_data.get('title') or member_data.get('login'),
                                     })
        
        response.setHeader("Content-type", "application/json")
        response.write(json.dumps(json_results))


class QueryGroupsView(BrowserView):
    """Query for esistings site members"""
    
    def __call__(self, *args, **kwargs):
        term = self.request.form.get('term', '')
        response = self.request.response
        
        acl_users = getToolByName(self.context, 'acl_users')
        
        results = list(acl_users.searchGroups(name=term))
        results += [x for x in acl_users.searchUsers(title=term) if x not in results]
        results = sorted(results, key=lambda m: m.get('title') or m.get('groupid'))

        json_results = []
        
        for data in results:
            json_results.append({'value': data.get('groupid'),
                                 'label': data.get('title') or data.get('groupid'),
                                 })
        
        response.setHeader("Content-type", "application/json")
        response.write(json.dumps(json_results))
