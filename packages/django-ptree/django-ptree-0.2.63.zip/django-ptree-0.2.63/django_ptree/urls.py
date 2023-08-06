from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    # url(r'^$', 'django_ptree.views.home', name='home'),
    # url(r'^django_ptree/', include('django_ptree.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

import ptree.urls
urlpatterns += ptree.urls.urlpatterns()
