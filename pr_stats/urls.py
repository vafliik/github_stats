from django.conf.urls import url

from . import views

app_name = 'pr_stats'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pr_number>[0-9]+)/$', views.detail, name='detail'),
    url(r'^pulls$', views.pulls, name='pulls'),
    url(r'^statistics', views.statistics, name='statistics'),
]