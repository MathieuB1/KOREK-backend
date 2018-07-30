from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response


from knap.models import Product, ProductImage
from knap.permissions import IsOwnerOrReadOnly
from knap.serializers import UserSerializerRegister, ProductSerializer, UserSerializer, ProductImageSerializer

from django.conf import settings

from django.contrib.auth import get_user_model

#Cache time to live 15 minutes
#CACHE_TTL = 60*15


#@cache_page(CACHE_TTL)
class ProductViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents KnapProduct.


    The **owner** of the product may update or delete instances.
 
    Try it yourself by logging in as one of these four users: **amy**.
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


class UserRegisterViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the users registration form.

    As you can see, the collection of of products instances owned by a user are
    serialized using a title representation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializerRegister

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

    

 
