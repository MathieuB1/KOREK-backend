import jwt
from django.contrib.auth.models import User, Group

from rest_framework import permissions, renderers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from korek.models import ProfileImage, Product, GroupAcknowlegment, Profile, PasswordReset, ProductImage, ProductVideo, ProductAudio, ProductFile, Category, Comment, ProductLocation

from korek.permissions import IsOwnerOrReadOnly, RegisterPermission, IsAuthentificatedOwnerOrReadOnly, GroupPermission, GroupAcknowlegmentPermission, PasswordPermission, ProfileImageViewSetPermission, CategoryPermission, CommentPermission, LocationPermission
from korek.serializers import ProfileImageSerializer, UserSerializerRegister, ProductSerializer, UserSerializer, ProductImageSerializer, ProductVideoSerializer, GroupSerializerOwner, GroupAcknowlegmentSerializer, PasswordSerializer, CategorySerializer, TagsSerializer, CommentSerializer, ProductLocationSerializer
from django.conf import settings
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.contrib.auth import get_user_model

from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.decorators import api_view

# Tags
from taggit.models import Tag

from django.db import connection


@api_view(('GET',))
def protectedMedia(request):

    response = HttpResponse(status=200)

    media_request = ''
    media_type = ''
    jwt_user = None

    # Check if product associated is private to owner
    try:

        media_request = '/'.join(request.path.split('/')[2:]).split('?')[0]
        media_type = media_request.split('/')[0]
        token = request.GET.get('token', False)
        
        if token:
            try:
                user_jwt = jwt.decode(token,settings.SECRET_KEY,)
                jwt_user = User.objects.get(id=user_jwt['user_id'])
            except:
                pass

        product = {}
        if media_type == 'Products_Image':
            product = ProductImage.objects.get(image=media_request).product
        elif media_type == 'Products_Video':
            product = ProductVideo.objects.get(video=media_request).product
        elif media_type == 'Products_Audio':
            product = ProductAudio.objects.get(audio=media_request).product
        else:
            product = ProductFile.objects.get(file=media_request).product

        if product.private and request.user != product.owner:
            if jwt_user != product.owner:
                return Response(status=403)

    except:
        return Response(status=403)


    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = '/protected/' + media_request
    
    # Check if user is in the same group
    if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
        # We want to retrieve a post media
        owner_id = request.path.split('/')[-2]
        user_owner = User.objects.get(id=owner_id)
        user_group = Profile.objects.get(user=user_owner)

        if request.user.is_authenticated:
            for group in request.user.groups.all():
                if str(user_group.user_group) == str(group):
                    return response

        elif jwt_user:
            for group in jwt_user.groups.all():
                if str(user_group.user_group) == str(group):
                    return response

        return Response(status=403)

    elif settings.PRIVACY_MODE[0].startswith('PUBLIC'):
        return response

    else:
        return Response(status=403)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API View that creates, updates and deletes a korek product

    This is the main feature! User can add/update/delete text data, media files, categories, tags, comments and geolocations. 
    User can also define private products.
    """
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('owner__username','category__name','tags__name')



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
    
        q_objects = Q()
        q_objects_likes = Q()
        limit_likes_queries = 10

        if self.request.query_params.get('barcode'):
            q_objects.add(Q(barcode=self.request.query_params.get('barcode')), Q.AND)
            q_objects_likes = q_objects

        if self.request.query_params.get('search'):
            q_objects.add(Q(search_vector=self.request.query_params.get('search')), Q.AND)
            q_objects_likes.add(Q(title__contains=self.request.query_params.get('search')) | Q(subtitle__contains=self.request.query_params.get('search')), Q.AND)

        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):

            users = []
            for group in self.request.user.groups.all():
                users.append(Profile.objects.get(user_group=group).user)

            tmp_query = Q(owner__in=users)
            q_objects.add(tmp_query, Q.AND)
            q_objects_likes.add(tmp_query, Q.AND)

            if self.request.user.is_authenticated:
                products = Product.objects.filter(q_objects).exclude(~Q(owner__in=[self.request.user]), private=True).order_by('created').reverse()
                products |= Product.objects.filter(q_objects_likes).exclude(~Q(owner__in=[self.request.user]), private=True).order_by('created').reverse()[:limit_likes_queries]
                return products
            else:
                return Product.objects.none()

        if self.request.user.is_authenticated:
            tmp_query = Q(owner__in=[self.request.user])
            q_objects.add(tmp_query, Q.AND)
            q_objects_likes.add(tmp_query, Q.AND)

        products = Product.objects.exclude(~Q(q_objects), private=True).order_by('created').reverse()
        products |= Product.objects.exclude(~Q(q_objects_likes), private=True).order_by('created').reverse()[:limit_likes_queries]
        return products



class UserRegisterViewSet(viewsets.ModelViewSet):
    """
    API View that creates, updates and deletes a korek user

    Anonymous users can create a new user & Logged in user can update/delete their account
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
        User.objects.filter(username=user).delete() # deleting the user and all data
        return super(UserRegisterViewSet, self).destroy(request, *args, **kwargs)

    
class GroupSerializerOwnerViewSet(viewsets.ModelViewSet):
    """
    API View that displays user groups

    Get groups owner
    """
    queryset = User.objects.none()
    serializer_class = GroupSerializerOwner
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          GroupPermission,)

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

class GroupAcknowlegmentViewSet(viewsets.ModelViewSet):
    """
    API View that lists friends requests

    User has to accept the request before being friends
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
    API View that provides the password renewal

    Valid EMAIL_HOST_USER and EMAIL_HOST_PASSWORD have to be defined in docker-compose file before using this feature
    """
    queryset = PasswordReset.objects.none()
    serializer_class = PasswordSerializer
    permission_classes = (PasswordPermission,)


class ProfileImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API View that provides friends list

    User can view all friends and can delete them
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
    """
    API View that provides a choice of categories

    User can retreive and add new categories
    """
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
    API View that provides a choice of tags

    User can retreive and add new tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (CategoryPermission,)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API View that displays user's comments

    User can retreive/delete his comments 
    """
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = (CommentPermission,)
    
    def get_queryset(self):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            if self.request.user.is_authenticated:
                return Comment.objects.filter(owner=self.request.user).order_by('created').reverse()
            else:
                return Comment.objects.none()
                
        return Comment.objects.all()

    def destroy(self, request, pk=None):
        comment = Comment.objects.get(id=pk)
        if comment.owner == self.request.user or \
           self.request.user == comment.product.owner:
            comment.delete()
            return Response(status=204)

        return Response(status=403)



class IntersectViewSet(viewsets.ModelViewSet):
    """
    API View that retreives a list of points within an area

    User can retreive locations defined in products by selecting them into a area.
    """
    queryset = ProductLocation.objects.none()
    serializer_class = ProductLocationSerializer
    permission_classes = (LocationPermission,)

    def get_queryset(self):
        locations = []

        bbox = self.request.GET.get('bbox','-180.00 90.00,180.00 90.00,180.00 -90.00,-180.00 -90.00').split(',')
        no_location = ProductLocation.objects.none()
        if len(bbox) == 4:
            try:
                for corner in bbox:
                    coordinates = corner.split(' ')
                    if float(coordinates[0]) >= -180 and float(coordinates[0]) <= 180 and float(coordinates[1]) >= -90 and float(coordinates[1]) <= 90:
                        pass
                    else:
                        return no_location
            except:
                return no_location
        else:
            return no_location
        
        tmp_query = "SELECT DISTINCT ON(product_id) product_id,id,created,ST_AsText(coords) FROM korek_productlocation WHERE " \
                "product_id IN (%s) AND ST_Intersects(geometry(coords), geometry(ST_GeomFromText('POLYGON((%s,%s))',4326))) = true ORDER BY product_id,id DESC"

        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            if self.request.user.is_authenticated:
                users = []
                for group in self.request.user.groups.all():
                    users.append(Profile.objects.get(user_group=group).user)
                products = Product.objects.filter(owner__in=users).exclude(~Q(owner__in=[self.request.user]), private=True).values_list('id')
                if products:
                    query = tmp_query % (str([el[0] for el in products])[1:-1], str(bbox)[1:-1].replace("'",""), bbox[0])
                    return ProductLocation.objects.raw(query)
                else:
                    return no_location
            else:
                return no_location

        else:
            if self.request.user.is_authenticated:
                products = Product.objects.exclude(~Q(owner__in=[self.request.user]), private=True).values_list('id')
            else:
                products = Product.objects.filter(private=False).values_list('id')
                
            query = tmp_query % (str([el[0] for el in products])[1:-1], str(bbox)[1:-1].replace("'",""), bbox[0])
            return ProductLocation.objects.raw(query)