from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from todolist.models import TodoList
from todolist.permissions import IsOwnerOrReadOnly
from todolist.serializers import TodoListSerializer, UserSerializer


class TodoListViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents TodoList.

    The `highlight` field presents a hyperlink to the highlighted HTML
    representation of a python snippet.

    The **owner** of the code snippet may update or delete instances
    of the code snippet.

    Try it yourself by logging in as one of these four users: **amy**, **max**,
    **jose** or **aziz**.  Passwords are the same as the usernames.
    """
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=(renderers.StaticHTMLRenderer,))
    def highlight(self, request, *args, **kwargs):
        """
        This entry doesn't work with swagger, please open directly the link through your webrowser.
        """
        todolist = self.get_object()
        return Response(todolist.highlighted)

    def perform_create(self, serializer):
        """
        This entry requires a pair of title and text 'python code is highlighted'.
        """
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users in the system.

    As you can see, the collection of todos instances owned by a user are
    serialized using a hyperlinked representation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer