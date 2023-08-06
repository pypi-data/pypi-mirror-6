from django.conf.urls import patterns, url
from filmmap import views

urlpatterns = patterns('',
        url(r'^api/v1/', views.api_v1, name='api_v1'),
        url(r'^', views.index, name='index'),
)
