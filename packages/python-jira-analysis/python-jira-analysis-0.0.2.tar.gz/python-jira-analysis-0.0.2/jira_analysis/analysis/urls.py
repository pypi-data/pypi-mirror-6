from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jira_analysis.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'analysis.views.main', name='main'),
    url(r'^infographics/(?P<project_id>\d+)/$', 'analysis.views.infographics', name='infographics'),
    url(r'^sample_all/', 'analysis.views.sample_all', name='sample_all'),
    url(r'^statuses/', 'analysis.views.statuses', name='statuses'),
    url(r'^admin/', include(admin.site.urls)),    
)
