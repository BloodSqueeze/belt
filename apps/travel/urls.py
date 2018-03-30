from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^logged$', views.logged),
    url(r'^logout$', views.logout),
    url(r'^add$', views.add),
    url(r'^create$', views.create),
    url(r'^enroll/(?P<trip_id>\d+)$', views.enroll),
    url(r'^show/(?P<trip_id>\d+)$', views.show),
]