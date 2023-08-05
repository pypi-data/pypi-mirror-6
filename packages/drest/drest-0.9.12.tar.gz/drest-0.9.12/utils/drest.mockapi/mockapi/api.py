
from django.contrib.auth.models import User

from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication
from tastypie.authentication import DigestAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import FormValidation
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource, ALL
from tastypie.api import Api
from tastypie.utils import trailing_slash

from mockapi.projects.models import Project

### READ ONLY API V0

class UserResource(ModelResource):    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'users'
        filtering = {
            'username': ALL,
            }
        allowed_methods = ['get']

class UserResourceViaApiKeyAuth(ModelResource):    
    class Meta:
        queryset = User.objects.all()
        authentication = ApiKeyAuthentication()
        resource_name = 'users_via_apikey_auth'
        filtering = {
            'label': ALL,
            }
        allowed_methods = ['get']
        
class UserResourceViaBasicAuth(ModelResource):    
    class Meta:
        queryset = User.objects.all()
        authentication = BasicAuthentication()
        resource_name = 'users_via_basic_auth'
        filtering = {
            'label': ALL,
            }
        allowed_methods = ['get']

class UserResourceViaDigestAuth(ModelResource):    
    class Meta:
        queryset = User.objects.all()
        authentication = DigestAuthentication()
        resource_name = 'users_via_digest_auth'
        filtering = {
            'label': ALL,
            }
        allowed_methods = ['get']
        
class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        authorization = Authorization()
        resource_name = 'projects'
        filtering = {
            'label': ALL,
            }
        allowed_methods = ['get', 'put', 'post', 'delete', 'patch']
        
v0_api = Api(api_name='v0')
v0_api.register(UserResource())
v0_api.register(UserResourceViaApiKeyAuth())
v0_api.register(UserResourceViaBasicAuth())
v0_api.register(UserResourceViaDigestAuth())
v0_api.register(ProjectResource())
