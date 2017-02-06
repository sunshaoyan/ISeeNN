from django.conf.urls import url

from . import views

app_name = 'image_server'

urlpatterns = [
    url(r'^get_image/(?P<id>[a-zA-Z0-9]{24})$', views.get_image, name='get_image'),
    url(r'^get_thumbnail/(?P<id>[a-zA-Z0-9]{24})$', views.get_thumbnail, name='get_thumbnail'),
]
