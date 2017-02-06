from django.conf.urls import url

from . import views

app_name = 'search_web'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.upload, name='upload'),
    # url(r'^result/$', views.result, name='result'),
    url(r'^get_image/(?P<id>[a-zA-Z0-9]{24})$', views.get_image, name='get_image'),
    url(r'^get_thumbnail/(?P<id>[a-zA-Z0-9]{24})$', views.get_thumbnail, name='get_thumbnail'),
    url(r'^user_image/(?P<id>[a-zA-Z0-9]{24})$', views.user_image, name='user_image'),
    url(r'^user_image/(?P<id>[a-zA-Z0-9]{24})/(?P<thumbnail>thumbnail)$', views.user_image, name='user_image_thumbnail'),
]