from django.contrib.auth.models import User, Group

from rest_framework import permissions, renderers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from korek.models import ProfileImage, Product, GroupAcknowlegment, Profile, PasswordReset, ProductImage, ProductVideo, ProductAudio, Category
from korek.permissions import IsOwnerOrReadOnly, RegisterPermission, IsAuthentificatedOwnerOrReadOnly, GroupPermission, GroupAcknowlegmentPermission, PasswordPermission, ProfileImageViewSetPermission, CategoryPermission
from korek.serializers import ProfileImageSerializer, UserSerializerRegister, ProductSerializer, UserSerializer, ProductImageSerializer, ProductVideoSerializer, GroupSerializerOwner, GroupAcknowlegmentSerializer, PasswordSerializer, CategorySerializer, TagsSerializer
from django.conf import settings
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.contrib.auth import get_user_model

from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.decorators import api_view

# Tags
from taggit.models import Tag

@api_view(('GET',))
def protectedMedia(request):

    response = HttpResponse(status=200)

    media_request = ''
    media_type = ''

    # Check if product associated is private to owner
    try:

        media_request = '/'.join(request.path.split('/')[2:])
        media_type = media_request.split('/')[0]

        product = {}
        if media_type == 'Products_Image':
            product = ProductImage.objects.get(image=media_request).product
        elif media_type == 'Products_Video':
            product = ProductVideo.objects.get(video=media_request).product
        elif media_type == 'Products_Audio':
            product = ProductAudio.objects.get(audio=media_request).product

        if product.private and (request.user != product.owner):
            return Response(status=403)
    except:
        return Response(status=403)


    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = '/protected/' + media_request
    
    # Check if user is in the same group
    if settings.PRIVACY_MODE[0].startswith('PRIVATE') and request.user.is_authenticated:

        # We want to retrieve a post media
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
    Try it yourself by logging in as one of these four users: **korek**.
    Passwords are the same as the usernames.
    """
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_fields = ('owner__username','category__name','tags__name')
    search_fields = ('title')


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

            return Product.objects.filter(owner__in=users).exclude(~Q(owner__in=[self.request.user]), private=True).order_by('created').reverse()

        return Product.objects.exclude(~Q(owner__in=[self.request.user]), private=True).order_by('created').reverse()



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
        user = request.user
        my_group = Profile.objects.get(user=user).user_group
        Group.objects.filter(name=my_group).delete() # deleting group
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


class ProfileImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users products in the system.
    """
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          ProfileImageViewSetPermission,)

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('profile__user__username',)

    def get_queryset(self):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            
            profiles = []
            for group in self.request.user.groups.all():
                profiles.append(Profile.objects.get(user_group=group))

            return ProfileImage.objects.filter(profile__in=profiles)

        return ProfileImage.objects.all()

    # Delete a Friend
    def destroy(self, request, pk):
        user = request.user
        my_group = Profile.objects.get(user=user).user_group

        profile_user_to_delete = ProfileImage.objects.get(id=pk).profile
        friend_group = profile_user_to_delete.user_group

        if friend_group != my_group:
            _group = Group.objects.get(name=friend_group) 
            _group.user_set.remove(user)
            
            _group = Group.objects.get(name=my_group) 
            _group.user_set.remove(profile_user_to_delete.user)

            return Response(status=204)

        return Response(status=403)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    permission_classes = (CategoryPermission,)

    def list(self, request):
        return Response(Category.dump_bulk(), status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        queryset = Category.get_tree().filter(depth=1, depth__isnull=True)
        operation = get_object_or_404(queryset, pk=pk)
        serializer = Category(operation, context={'request': request})

        return Response(serializer.data)

    def update(self, request, pk=None):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        get(pk).delete()

        return Response(Category.dump_bulk())


class TagViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents Korek Tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (CategoryPermission,)