from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from knap import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet)
# Adding the knap view
router.register(r'products', views.ProductViewSet)


schema_view = get_swagger_view(title='KNAP API')

urlpatterns = [
    # Swagger
    url('^$', schema_view),
    url(r'^', include(router.urls)),
    # Usual Rest API
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]