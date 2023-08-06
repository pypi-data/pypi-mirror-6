from django.conf.urls import patterns, url

from handlers import PlacesHandler, PlaceIdHandler, ReviewsHandler, ReviewIdHandler, PhotosHandler, PhotoIdHandler

urlpatterns = patterns('',
                       
    # Places.
    url(r'^/?$', PlacesHandler.as_view(), name='index'),
    url(r'^/(?P<pk>[0-9]+)/?$', PlaceIdHandler.as_view(), name='id'),
    url(r'^/(?P<pk>[0-9]+)/photos/?$', PhotosHandler.as_view(), name='photos'),
    url(r'^/(?P<pk>[0-9]+)/photos/(?P<photo_pk>[0-9]+)/?$', PhotoIdHandler.as_view(), name='photo_id'),
    url(r'^/(?P<pk>[0-9]+)/reviews/?$', ReviewsHandler.as_view(), name='reviews'),
    url(r'^/(?P<pk>[0-9]+)/reviews/(?P<review_pk>[0-9]+)/?$', ReviewIdHandler.as_view(), name='review_id')
)