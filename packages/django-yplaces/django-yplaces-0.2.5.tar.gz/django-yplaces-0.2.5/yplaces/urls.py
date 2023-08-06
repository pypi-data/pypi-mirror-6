from django.conf.urls import patterns, url

import views

js_info_dict = {
    'packages': ('yplaces',),
}

urlpatterns = patterns('',
    url(r'^/?$', views.index, name='index'),
    url(r'^/add/?$', views.add, name='add'),
    url(r'^/jsi18n/?$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jsi18n'),
    url(r'^/search/?$', views.search, name='search'),
    url(r'^/(?P<pk>[0-9]+)/?$', views.place_id, name='id'),
    url(r'^/(?P<pk>[0-9]+)/(?P<slug>[a-zA-Z0-9-]+)/?$', views.place_slug, name='slug'),
    url(r'^/(?P<pk>[0-9]+)/(?P<slug>[a-zA-Z0-9-]+)/edit/?$', views.edit, name='edit'),
    url(r'^/(?P<pk>[0-9]+)/(?P<slug>[a-zA-Z0-9-]+)/photos/?$', views.photos, name='photos')
)