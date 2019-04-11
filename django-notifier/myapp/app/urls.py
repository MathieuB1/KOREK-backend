from django.conf.urls import include, url

urlpatterns = [
    url(r'^event/', include('event.urls')),
]