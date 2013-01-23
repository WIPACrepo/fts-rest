from django.conf.urls.defaults import *
from ping import ping
from resources import ConfigAuditResource, FileResource, JobResource
from resources import LinkResource, MemberResource, SeResource, ShareResource
from tastypie.api import Api
import delegation


def override_urls(self):
	return [
		url(r'^(?P<api_name>%s)/ping/?$' % self.api_name, ping),
		url(r'^(?P<api_name>%s)/delegation/' % self.api_name, include(delegation.urls))
	]
	
Api.override_urls = override_urls

full_api = Api(api_name = 'v1')
full_api.register(ConfigAuditResource())
full_api.register(FileResource())
full_api.register(JobResource())
full_api.register(LinkResource())
full_api.register(MemberResource())
full_api.register(SeResource())
full_api.register(ShareResource())

urlpatterns = patterns('',
	(r'', include(full_api.urls))
)
