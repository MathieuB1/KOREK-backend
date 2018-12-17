from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view
from django.contrib import admin

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

from korek import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet)
# Adding the KOREK view
router.register(r'products', views.ProductViewSet)
router.register(r'register', views.UserRegisterViewSet, base_name='user-register')
router.register(r'groups', views.GroupSerializerOwnerViewSet)
router.register(r'acknowlegment', views.GroupAcknowlegmentViewSet)



urlpatterns1 = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    # Usual Rest API
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^media/', views.protectedMedia, name="protect_media"),
]

schema_view = get_swagger_view(title='KOREK API', patterns=urlpatterns1)

# Mask this pattern to swagger
urlpatterns = [
    # Swagger
    url(r'^$', schema_view),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
] + urlpatterns1