from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^projects/', include('agency.project.urls')),
    )
