from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view


from todolist import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet)
# Adding the TodoList view
router.register(r'todolist', views.TodoListViewSet)

schema_view = get_swagger_view(title='TodoList API')

urlpatterns = [
    # Swagger
    url('^$', schema_view),
    url(r'^', include(router.urls)),
    # Usual Rest API
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
