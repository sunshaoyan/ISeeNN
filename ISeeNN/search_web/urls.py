from django.conf.urls import url

from . import views

app_name = 'search_web'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.upload, name='upload'),
    # The following url dispatchers are ugly. Revise them.
    url(r'^result/(?P<id>[a-zA-Z0-9]{24})$', views.result, name='result'),
    url(r'^result/(?P<id>[a-zA-Z0-9]{24})/(?P<from_db>from_db)$', views.result, name='result_from_db'),
    url(r'^result/(?P<id>[a-zA-Z0-9]{24})/(?P<re_rank>re_rank)$', views.result, name='result_re_rank'),
    url(r'^result/(?P<id>[a-zA-Z0-9]{24})/(?P<re_rank>re_rank)/(?P<from_db>from_db)$', views.result, name='result_re_rank_from_db'),
    url(r'^get_image/(?P<id>[a-zA-Z0-9]{24})$', views.get_image, name='get_image'),
    url(r'^get_thumbnail/(?P<id>[a-zA-Z0-9]{24})$', views.get_thumbnail, name='get_thumbnail'),
    url(r'^user_image/(?P<id>[a-zA-Z0-9]{24})$', views.user_image, name='user_image'),
    url(r'^user_image/(?P<id>[a-zA-Z0-9]{24})/(?P<thumbnail>thumbnail)$', views.user_image, name='user_image_thumbnail'),
    url(r'^detail/(?P<image_id>[a-zA-Z0-9]{24})/(?P<user_upload_id>[a-zA-Z0-9]{24})$',
        views.detail, name='detail'),
    url(r'^detail/(?P<image_id>[a-zA-Z0-9]{24})/(?P<user_upload_id>[a-zA-Z0-9]{24})/(?P<from_db>from_db)$',
        views.detail, name='detail_from_db'),
]