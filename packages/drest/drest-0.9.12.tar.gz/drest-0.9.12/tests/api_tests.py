"""Tests for drest.api."""

import os
import unittest
from nose.tools import ok_, eq_, raises

import drest
from drest.testing import MOCKAPI

api = drest.api.API(MOCKAPI)

class MyAPI(drest.api.TastyPieAPI):
    class Meta:
        baseurl = MOCKAPI
        extra_headers = dict(foo='bar')
        extra_params = dict(foo2='bar2')
        extra_url_params = dict(foo3='bar3')
        
class APITestCase(unittest.TestCase):
    def test_auth(self):
        api.auth('john.doe', 'password')
        eq_(api.request._auth_credentials[0], 'john.doe')
        eq_(api.request._auth_credentials[1], 'password')
    
    def test_custom_auth(self):
        class MyAPI(drest.API):
            def auth(self, *args, **kw):
                for key in kw:
                    self.request.add_url_param(key, kw[key])
        myapi = MyAPI(MOCKAPI)
        myapi.auth(user='john.doe', password='password')
        eq_(myapi.request._extra_url_params['user'], 'john.doe')
        eq_(myapi.request._extra_url_params['password'], 'password')

    def test_wrapped_meta(self):
        class MyAPI2(drest.api.TastyPieAPI):
            class Meta:
                trailing_slash = False

        myapi = MyAPI2(MOCKAPI)
        eq_(myapi.request._meta.trailing_slash, False)
    
    def test_extra_headers(self):
        api = MyAPI()
        eq_('bar', api.request._extra_headers['foo'])
    
    def test_extra_params(self):
        api = MyAPI()
        eq_('bar2', api.request._extra_params['foo2'])
    
    def test_extra_url_params(self):
        api = MyAPI()
        eq_('bar3', api.request._extra_url_params['foo3'])
    
    def test_request(self):
        response = api.make_request('GET', '/')
        res = 'users' in response.data
        ok_(res)

    def test_add_resource(self):
        api.add_resource('users')
        response = api.users.get()
    
        api.add_resource('users2', path='/users/')
        response = api.users2.get()
    
        api.add_resource('users3', path='/users/', 
                         resource_handler=drest.resource.RESTResourceHandler)
        response = api.users3.get()
    
    @raises(drest.exc.dRestResourceError)
    def test_duplicate_resource(self):
        api.add_resource('users')

    @raises(drest.exc.dRestResourceError)
    def test_bad_resource_name(self):
        api.add_resource('some!bogus-name')

    def test_nested_resource_name(self):
        api.add_resource('nested.users.resource', path='/users/')
        eq_(api.nested.__class__, drest.resource.NestedResource)
        eq_(api.nested.users.__class__, drest.resource.NestedResource)
        eq_(api.nested.users.resource.__class__, drest.resource.RESTResourceHandler)
    
    def test_tastypieapi_via_apikey_auth(self):
        api = drest.api.TastyPieAPI(MOCKAPI)
        api.auth(user='john.doe', api_key='JOHN_DOE_API_KEY')
    
        # verify headers
        eq_(api.request._extra_headers, 
            {'Content-Type': 'application/json', 
             'Authorization': 'ApiKey john.doe:JOHN_DOE_API_KEY'})
    
        # verify resources
        res = 'users' in api.resources
        ok_(res)
        res = 'projects' in api.resources
        ok_(res)
    
        # and requests
        response = api.users_via_apikey_auth.get()
        eq_(response.data['objects'][0]['username'], 'admin')
    
        response = api.projects.get(params=dict(label__startswith='Test Project'))
        ok_(response.data['objects'][0]['label'].startswith('Test Project'))

    def test_tastypieapi_via_basic_auth(self):
        api = drest.api.TastyPieAPI(MOCKAPI, auth_mech='basic')
        api.auth(user='john.doe', password='password')

        eq_(api.request._auth_credentials[0], 'john.doe')
        eq_(api.request._auth_credentials[1], 'password')
    
        # verify resources
        res = 'users' in api.resources
        ok_(res)
        res = 'projects' in api.resources
        ok_(res)
    
        # and requests
        response = api.users_via_basic_auth.get()
        eq_(response.data['objects'][0]['username'], 'admin')

    @raises(drest.exc.dRestAPIError)
    def test_tastypieapi_via_unknown_auth(self):
        api = drest.api.TastyPieAPI(MOCKAPI, auth_mech='bogus')
        api.auth(user='john.doe', password='password')
