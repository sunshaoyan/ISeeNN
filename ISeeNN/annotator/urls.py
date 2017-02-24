from django.conf.urls import url

from . import views

app_name = 'annotator'

urlpatterns = [
    url(r'^select$', views.select, name='select'),
    url(r'^select/(?P<image_id>[a-zA-Z0-9]{24})$', views.select, name='select_id'),
    url(r'^confirm_select/(?P<image_id>[a-zA-Z0-9]{24})$', views.confirm_select, name='confirm_select'),
    url(r'^view_selected$', views.view_selected, name='view_selected'),
    url(r'^view_selected_detail/(?P<query_id>[a-zA-Z0-9]{24})$', views.view_selected_detail, name='view_selected_detail'),
    url(r'^remove_select/(?P<query_id>[a-zA-Z0-9]{24})$', views.remove_select, name='remove_select'),

    url(r'^login$', views.login, name='login'),
    url(r'^login/(?P<error>[0-3])$', views.login, name='login_error'),
    url(r'^login/(?P<info>[8])$', views.login, name='login_info'),
    url(r'^login_submit$', views.login_submit, name='login_submit'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^annotate$', views.annotate, name='annotate'),
    url(r'^annotate_submit$', views.annotate_submit, name='annotate_submit'),
]