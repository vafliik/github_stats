from django.conf.urls import url

from . import views

app_name = 'pr_stats'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pr_number>[0-9]+)/$', views.detail, name='detail'),
    url(r'^pulls$', views.pulls, name='pulls'),
    url(r'^pulls_all$', views.pulls_all, name='pulls_all'),
    url(r'^statistics/(?P<year>\d{4})/(?P<month>\d{0,2})/(?P<day>\d+)/$', views.statistics, name='statistics'),
    url(r'^statistics', views.statistics, name='statistics-basic'),
]