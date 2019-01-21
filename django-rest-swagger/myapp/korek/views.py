from django.contrib.auth.models import User, Group

from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from korek.models import Product, GroupAcknowlegment, Profile, PasswordReset
from korek.permissions import IsOwnerOrReadOnly, RegisterPermission, IsAuthentificatedOwnerOrReadOnly, GroupPermission, GroupAcknowlegmentPermission, PasswordPermission
from korek.serializers import UserSerializerRegister, ProductSerializer, UserSerializer, ProductImageSerializer, ProductVideoSerializer, GroupSerializerOwner, GroupAcknowlegmentSerializer, PasswordSerializer
from django.conf import settings

from django.contrib.auth import get_user_model

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.decorators import api_view



@api_view()
def protectedMedia(request):

    response = HttpResponse(status=200)
    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = '/protected/' + '/'.join(request.path.split('/')[2:])

    if settings.PRIVACY_MODE[0].startswith('PRIVATE') and request.user.is_authenticated:

        owner_id = request.path.split('/')[-2]
        user_owner = User.objects.get(id=owner_id)
        user_group = Profile.objects.get(user=user_owner)

        for group in request.user.groups.all():
            if str(user_group.user_group) == str(group):
                return response

        return Response(status=403)

    elif settings.PRIVACY_MODE[0].startswith('PUBLIC'):
        return response

    else:
        return Response(status=403)



class ProductViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents KorekProduct.

    The **owner** of the product may update or delete instances.
    Try it yourself by logging in as one of these four users: **korek** **amy**.
    Passwords are the same as the usernames.
    """
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @action(renderer_classes=[renderers.StaticHTMLRenderer], detail=True)
    def highlight(self, request, *args, **kwargs):
        product = self.get_object()
        return Response(product.highlight)

    def perform_create(self, serializer):
        """
        This entry requires a pair of title and text
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):

            users = []
            for group in self.request.user.groups.all():
                users.append(Profile.objects.get(user_group=group).user)
            return Product.objects.filter(owner__in=users)

        return Product.objects.all()



class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users products in the system.
    """
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthentificatedOwnerOrReadOnly,)
  

    def get_queryset(self):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            
            users = []
            for group in self.request.user.groups.all():
                users.append(Profile.objects.get(user_group=group).user)

            return User.objects.filter(username__in=users)

        #return User.objects.filter(username=self.request.user.username)
        return User.objects.all()


class UserRegisterViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the users registration form.
    """
    queryset = User.objects.none()
    serializer_class = UserSerializerRegister
    permission_classes = (RegisterPermission,)

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

    def destroy(self, request, *args, **kwargs):
        user = request.user # deleting user
        self.request.user.groups.first().delete() # deleting group
        return super(UserRegisterViewSet, self).destroy(request, *args, **kwargs)

    
class GroupSerializerOwnerViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the groups form.
    """
    queryset = User.objects.none()
    serializer_class = GroupSerializerOwner
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          GroupPermission,)

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)


class GroupAcknowlegmentViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the groups acknowlegment form.
    """
    queryset = GroupAcknowlegment.objects.none()
    serializer_class = GroupAcknowlegmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          GroupAcknowlegmentPermission,)

    def get_queryset(self):
        return GroupAcknowlegment.objects.filter(group_owner=self.request.user)


@api_view(['GET'])
def reset_password(request):

    parameters = request.path.split('&mail=')
    
    if len(parameters) > 1:
        user_mail = parameters[1]
        user_owner = User.objects.get(email=user_mail)

        if user_owner is not None:
            new_pass = PasswordReset.objects.get(tmp_url=str(request.META['HTTP_HOST']) + request.path)
            user_owner.set_password(new_pass.password)
            user_owner.save()

            PasswordReset.objects.filter(user_email=user_mail).delete()

            return Response(status=200)

    return HttpResponseRedirect('/')


class PasswordResetViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the reset password form.
    """
    queryset = PasswordReset.objects.none()
    serializer_class = PasswordSerializer
    permission_classes = (PasswordPermission,)