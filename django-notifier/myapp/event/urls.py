from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.notification, name='notification'),
    url(r'^notif/$', views.notif, name='notif'),
]