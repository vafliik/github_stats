from django.conf.urls import url

from . import views

app_name = 'pr_stats'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pr_number>[0-9]+)/$', views.detail, name='detail'),
    url(r'^pulls$', views.pulls, name='pulls'),
    url(r'^report$', views.report, name='report'),
    url(u'^pulls_all/(?P<q>.*)/$', views.pulls_all, name='pulls_all'),  # set range /pulls_all/2016-08-20..2016-08-27/
    url(r'^statistics/(?P<year>\d{4})/(?P<month>\d{0,2})/(?P<day>\d+)/$', views.statistics, name='statistics'),
    url(r'^statistics', views.statistics, name='statistics-basic'),
]