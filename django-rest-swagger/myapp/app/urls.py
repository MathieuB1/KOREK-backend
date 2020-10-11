from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

from korek import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



router = DefaultRouter()
# Adding the KOREK view
router.register(r'products', views.ProductViewSet)
router.register(r'register', views.UserRegisterViewSet, basename='user-register')
router.register(r'groups', views.GroupSerializerOwnerViewSet)
router.register(r'acknowlegment', views.GroupAcknowlegmentViewSet)
router.register(r'password_reset', views.PasswordResetViewSet)
router.register(r'profiles', views.ProfileImageViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'comment', views.CommentViewSet)

urlpatterns1 = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    # Usual Rest API
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
]

schema_view = get_schema_view(
   openapi.Info(
      title="Korek API",
      default_version='v1',
      description="A Django Rest Storage System",
      #terms_of_service="https://www.google.com/policies/terms/",
      #contact=openapi.Contact(email="korek@gmail.com"),
      #license=openapi.License(name="BSD License"),
   ),
   public=False,
   permission_classes=(permissions.AllowAny,),
   patterns=urlpatterns1
   
)

# Mask this pattern to swagger
urlpatterns = [
    # Swagger
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^media/', views.protectedMedia, name="protect_media"),
    url(r'^reset_password/', views.reset_password, name="reset_password"),
] + urlpatterns1