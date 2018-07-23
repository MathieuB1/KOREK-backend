from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response


from knap.models import Product, ProductImage
from knap.permissions import IsOwnerOrReadOnly
from knap.serializers import ProductSerializer, UserSerializer, ProductImageSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents KnapProduct.


    The **owner** of the code snippet may update or delete instances
    of the code snippet.

    Try it yourself by logging in as one of these four users: **amy**, **aziz**.
    Passwords are the same as the usernames.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        product = self.get_object()
        return Response(product.highlighted)

    def perform_create(self, serializer):
        """
        This entry requires a pair of title and text
        """
        serializer.save(owner=self.request.user)



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users in the system.

    As you can see, the collection of of products instances owned by a user are
    serialized using a title representation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer