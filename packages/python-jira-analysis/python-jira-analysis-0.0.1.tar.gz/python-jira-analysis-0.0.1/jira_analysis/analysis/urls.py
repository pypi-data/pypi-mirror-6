from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jira_analysis.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'analysis.views.main', name='main'),
    url(r'^infographics/', 'analysis.views.main', name='infographics'),

    url(r'^admin/', include(admin.site.urls)),    
)
