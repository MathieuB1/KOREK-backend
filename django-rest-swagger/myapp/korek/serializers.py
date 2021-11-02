from rest_framework import serializers
from korek.models import Product, ProductImage, ProductVideo, ProductAudio, ProductFile, Profile, GroupAcknowlegment, PasswordReset, ProfileImage, Category, Comment, ProductLocation
from django.contrib.auth.models import User, Group

import magic
import re
import datetime

from django.db import transaction
from collections import OrderedDict

from base64 import b64encode
from os import urandom

from django.conf import settings

from django.core.mail import send_mail

# Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Tags
from taggit.models import Tag
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from django.db.models import Count

from django.core.exceptions import PermissionDenied
import mimetypes

from django.db import connection

import json
import math

def guess_type(file_object):
    mime = magic.from_buffer(file_object.read()[:1024], mime=True).split('/')[0]
    if mime == 'application':
        mime = mimetypes.MimeTypes().guess_type(file_object.read()[:1024])[0].split('/')[0]
    return mime

def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

 # Ignore some validated Fields
class validated_entries(object):
    val = ""
    def __init__(self, initial_data, list_to_ignore):
        for key in initial_data:
            if key not in list_to_ignore:
                self.val += key + "=validated_data.get('" + key + "'),"
    def get_string(self):
            return self.val

############# KOREK SERIALISERS ##############
class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordReset
        fields = ('user_email','password',)
        write_only_fields = ('password',)

    def validate_user_email(self, value):
        if User.objects.filter(email=value).count() == 0:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def to_representation(self, obj):
        ret = super(PasswordSerializer, self).to_representation(obj)
        ret.pop('password')
        return ret

    def create(self, validated_data):

            PasswordReset.objects.filter(user_email=validated_data['user_email']).delete()

            tmp_url = str(self.context.get('view').request.META['HTTP_HOST'])  + '/reset_password/'+ str(b64encode(urandom(1024)).decode('utf-8')) + '&mail=' + str(validated_data['user_email'])
            password_reset = PasswordReset.objects.create(
                user_email = validated_data['user_email'],
                tmp_url = tmp_url,
                password = validated_data['password'])

            # Email is not mandatory
            if settings.EMAIL_HOST_USER[0] != 'xxxx.yyy@gmail.com':
                send_mail(
                    'Reset Password',
                    '',
                    settings.EMAIL_HOST_USER[0],
                    [validated_data['user_email']],
                    html_message = '<p>Click on this link to reset your password:</p><a href="' + tmp_url + '">Reset Password</a>',
                    fail_silently=False,
                )

            password_reset.save()
            return password_reset


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)
        extra_kwargs = {
            'name': {'validators': []},
        }


class RequiredFieldsMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields_notrequired = getattr(self.Meta, 'fields_notrequired', None)

        if fields_notrequired:
            for key in self.fields:
                if key in fields_notrequired:
                    self.fields[key].required = False

class UserSerializerRegister(RequiredFieldsMixin, serializers.ModelSerializer):
    groups = GroupSerializer(many=True, required=False, read_only=True)
    my_group = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, obj):
        ret = super(UserSerializerRegister, self).to_representation(obj)
        ret.pop('password')
        return ret
        

    def get_my_group (self, obj):
        if obj.username is not None:
            user = User.objects.get(username=obj.username)
            return Profile.objects.get(user=user).user_group

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name','my_group','groups',)
        fields_notrequired = ('password',)
        read_only_fields = ('id',)

    # Need to remove groups
    def validate_email(self, value):
        if value is None or value == '':
            raise serializers.ValidationError("Enter a valid email address.")

        try:
            user = User.objects.get(email=value)
            if self.instance and self.instance.id == user.id:
                return value
        except User.DoesNotExist:
            return value
        
        raise serializers.ValidationError("Email already exists.")

    def validate_password(self, value):
        if value is None or value == '':
            raise serializers.ValidationError("Enter a valid password.")
        if len(value) < 4:
            raise serializers.ValidationError("Password too short.")

        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)


        if validated_data.get('password') is not None:
            instance.set_password(validated_data['password'])

        # Update my Image
        images_data = {}
        for filename, file in  self.context.get('view').request.FILES.items():
            file_object = self.context.get('view').request.FILES[filename]
            profile = Profile.objects.get(user=self.context['request'].user)

            ProfileImage.objects.get(profile=profile).delete(False)
            ProfileImage.objects.create(profile=profile, image=file_object)
            break

        instance.save()
        return instance

    def create(self, validated_data):

        if validated_data.get('email') is None:
            raise serializers.ValidationError("Enter a valid email address.")
        if validated_data.get('password') is None:
            raise serializers.ValidationError("Enter a valid password.")

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name',''),
            last_name=validated_data.get('last_name','')
        )

        user.set_password(validated_data['password'])

        # Create a group for user
        new_group = Group.objects.create(name=b64encode(urandom(256)).decode('utf-8')[10:90])
        new_group.user_set.add(user)
        profile = Profile.objects.create(user=user, user_group=new_group)

        # Save my Image
        images_data = {}
        ProfileImage.objects.create(profile=profile)
        for filename, file in  self.context.get('view').request.FILES.items():
            file_object = self.context.get('view').request.FILES[filename]
            ProfileImage.objects.get(profile=profile).delete(False)
            ProfileImage.objects.create(profile=profile, image=file_object)
            break

        user.save()
        return user


class CommonTool:
    
    download_image = 'data:image/png;base64,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'

    def set_media_type(self, input_media,
                             images_data,
                             videos_data,
                             audios_data,
                             files_data):
        
        for filename, file in  input_media:
            file_object = self.context.get('view').request.FILES[filename]
            ext = file_object.name.split('.')[-1].lower()

            if ext in self.EXT_IMAGE_LIST:
                try:
                    file_type = guess_type(file_object)
                    if file_type == 'image':
                        images_data[file_object.name] = file_object
                except:
                    pass

            elif ext in self.EXT_VIDEO_LIST:
                try:
                    file_type = guess_type(file_object)
                    if file_type == 'video':
                        videos_data[file_object.name] = file_object
                except:
                    pass

            elif ext in self.EXT_AUDIO_LIST:
                try:
                    file_type = guess_type(file_object)
                    if file_type == 'audio':
                        audios_data[file_object.name] = file_object
                except:
                    pass
            else:
                try:
                    files_data[file_object.name] = file_object
                except:
                    pass
   
    def get_owner_image(self, obj):
        profile_owner = Profile.objects.get(user=User.objects.get(username=obj.owner))
        return ProfileImage.objects.get(profile=profile_owner).image

    def send_notification(self, user, message, id=None):
    
        channel_layer = get_channel_layer()
        
        # adding id to notification message
        message = str(id) + ";" + message

        if (id is None):
            # send to me only
            event = 'event_%s' % (user)
            async_to_sync(channel_layer.group_send)(event, {"type": "event_message", "message":  message })
        else:
            # send the notif to all friends
            profiles = []
            for group in user.groups.all():
                profiles.append(Profile.objects.get(user_group=group))

            for el in profiles:
                event = 'event_%s' % (el.user)
                async_to_sync(channel_layer.group_send)(event, {"type": "event_message", "message":  message })


        

class CommentSerializer(serializers.ModelSerializer, CommonTool):

    owner = serializers.ReadOnlyField(source='owner.username')
    owner_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id','product','owner','comment','created','owner_image')
        read_only_fields = ('id','owner','created','owner_image')

    def get_owner_image(self, obj):
        return CommonTool.get_owner_image(self, obj)

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.product = validated_data.get('product', instance.product)
        instance.comment = validated_data.get('comment', instance.comment)
        
        if instance.product.owner == instance.owner:
            instance.save()
            return instance

        raise PermissionDenied()

    def create(self, validated_data):
        comment = validated_data.get('comment','')
        product_input = validated_data.get('product', None)

        if settings.PRIVACY_MODE[0] == 'PUBLIC':
            comment = Comment.objects.create(product=product_input, owner=self.context.get('request').user, comment=comment)
            return comment    
        
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            
            owner_group = Profile.objects.get(user=product_input.owner).user_group

            # If user is the owner OR If user is a friend & not private product
            if self.context.get('request').user == product_input.owner or \
               not product_input.private and self.context.get('request').user.groups.filter(name=owner_group).exists():

                comment = Comment.objects.create(product=product_input, owner=self.context.get('request').user, comment=comment)
                return comment              

            raise PermissionDenied()


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLocation
        fields = ('created','coords',)

class ProductLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLocation
        fields = ('product','created','coords')
        read_only_fields = ('product','created','coords')


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, max_length=None, use_url=True,  style={'autofocus': True, 'placeholder': ''})

    class Meta:
        model = ProductImage
        fields = ('image',)


class ProductVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(required=False, max_length=None, use_url=True,  style={'placeholder': ''})

    class Meta:
        model = ProductVideo
        fields = ('video',)

class ProductAudioSerializer(serializers.ModelSerializer):
    audio = serializers.FileField(required=False, max_length=None, use_url=True,  style={'placeholder': ''})

    class Meta:
        model = ProductAudio
        fields = ('audio',)

class ProductFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, max_length=None, use_url=True,  style={'placeholder': ''})

    class Meta:
        model = ProductFile
        fields = ('file',)


class ProductSerializer(TaggitSerializer, serializers.ModelSerializer, CommonTool):
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_image = serializers.SerializerMethodField(read_only=True)

    images = ProductImageSerializer(source='productimage_set', required=False, many=True)
    videos = ProductVideoSerializer(source='productvideo_set', required=False, many=True)
    audios = ProductAudioSerializer(source='productaudio_set', required=False, many=True)
    files = ProductFileSerializer(source='productfile_set', required=False, many=True)

    barcode =  serializers.IntegerField(required=False, style={'hide_label': False, 'placeholder': '0'})

    highlight = serializers.HyperlinkedIdentityField(view_name='product-highlight', format='html', read_only=True)

    tags = TagListSerializerField(required=False)

    comments = serializers.SerializerMethodField()

    locations = LocationSerializer(source='productlocation_set', required=False, many=True)
    locations_distance = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('url', 'id', 'created', 'highlight', 'title', 'subtitle', 'text', 'barcode', 'price', \
                  'brand', 'owner','owner_image', 'language','images','videos','audios','files','private', \
                  'category','tags','comments', 'locations', 'locations_distance')

        extra_kwargs = {
            'images_urls': {'validators': []},
            'videos_urls': {'validators': []},
            'audios_urls': {'validators': []},
            'files_urls': {'validators': []},
            'locations_all': {'validators': []},
        }

    # Lookup tables
    EXT_IMAGE_LIST = ['gif','png','jpg','bmp','jpe','jpeg','tif','tiff']
    EXT_VIDEO_LIST = ['mkv','avi','mp4','flv','mpeg','wmv','mov','webm','ogg']
    EXT_AUDIO_LIST = ['mp3','ogg','wav']

    def to_representation(self, obj):
        ret = super(ProductSerializer, self).to_representation(obj)
        if obj.category and obj.category.name:
            ret['category'] = obj.category.name

        if self.context.get('view').request.GET.get('zip', '') == 'true':
            ret = OrderedDict({'id' : ret['id']})
        return ret

    def validate_locations(self, value):
        for el in value:
            if not isinstance(el,dict) or 'coords' not in el.keys():
                raise serializers.ValidationError('please use this syntax [{"coords": [6.627231, 43.541580]}]')

            for coord in el['coords']:
                if not isinstance(coord, float):
                    raise serializers.ValidationError("%s is not a valid location." % el['coords'])
        return value


    def get_comments(self,obj):
         product_comment = Comment.objects.filter(product=obj.id).order_by('-created')
         serializer = CommentSerializer(product_comment,many=True)
         return serializer.data

    def get_owner_image(self, obj):
        return CommonTool.get_owner_image(self, obj)

    def get_locations_distance(self,obj):
        last_coord = 0
        distance = 0.00
        for el in ProductLocation.objects.filter(product=obj.id):
            if last_coord != 0:
                distance += haversine(last_coord, el.coords.tuple)
            last_coord = el.coords.tuple
        return float("%.2f" % distance)

    def update(self, instance, validated_data):
        
        # Delete Media
        if self._kwargs['data'].get('images_urls', None) is not None or \
           self._kwargs['data'].get('videos_urls', None) is not None or \
           self._kwargs['data'].get('audios_urls', None) is not None or \
           self._kwargs['data'].get('files_urls', None) is not None:

            channel_layer = get_channel_layer()
            product_highlight = Product.objects.get(id=instance.id).highlight

            if self._kwargs['data'].get('images_urls', None) is not None:
                for el in self._kwargs['data']['images_urls']:
                    try:
                        image_name = el.split(settings.MEDIA_URL)[1]

                        ProductImage.objects.get(image=image_name).delete()

                        regex = re.compile(r'(<img src="' + settings.MEDIA_URL + image_name + '"/>)')
                        replaced = regex.sub(r"", product_highlight, 1)

                        product_highlight = replaced
                        Product.objects.filter(id=instance.id).update(highlight=replaced)

                        CommonTool.send_notification(self, self.instance.owner, "image deleted!", instance.id)

                    except:
                        pass
                

            if self._kwargs['data'].get('videos_urls', None) is not None:
                for el in self._kwargs['data']['videos_urls']:
                    try:
                        video_name = el.split(settings.MEDIA_URL)[1]

                        ProductVideo.objects.get(video=video_name).delete()

                        regex = re.compile(r'(<video controls><source src="' + settings.MEDIA_URL + video_name + '"/></video>)')
                        replaced = regex.sub(r"", product_highlight, 1)

                        product_highlight = replaced
                        Product.objects.filter(id=instance.id).update(highlight=replaced)

                        CommonTool.send_notification(self, self.instance.owner, "video deleted!", instance.id)

                    except:
                        pass


            if self._kwargs['data'].get('audios_urls', None) is not None:
                for el in self._kwargs['data']['audios_urls']:
                    try:
                        audio_name = el.split(settings.MEDIA_URL)[1]

                        ProductAudio.objects.get(audio=audio_name).delete()

                        regex = re.compile(r'(<audio controls><source src="' + settings.MEDIA_URL + audio_name + '"/></audio>)')
                        replaced = regex.sub(r"", product_highlight, 1)

                        product_highlight = replaced
                        Product.objects.filter(id=instance.id).update(highlight=replaced)

                        CommonTool.send_notification(self, self.instance.owner, "audio deleted!", instance.id)

                    except:
                        pass


            if self._kwargs['data'].get('files_urls', None) is not None:
                for el in self._kwargs['data']['files_urls']:
                    try:
                        file_name = el.split(settings.MEDIA_URL)[1]

                        ProductFile.objects.get(file=file_name).delete()

                        regex = re.compile(r'(<a href="' + settings.MEDIA_URL + file_name + '" download><img src=".*?" alt="download"></a>)')
                        replaced = regex.sub(r"", product_highlight, 1)

                        product_highlight = replaced
                        Product.objects.filter(id=instance.id).update(highlight=replaced)

                        CommonTool.send_notification(self, self.instance.owner, "file deleted!", instance.id)

                    except:
                        pass

            return instance

        # Delete Locations
        if self._kwargs['data'].get('locations_all', None) is not None :
            deleted = False
            action = self._kwargs['data']['locations_all'][0]

            if  action == 'delete':
                ProductLocation.objects.filter(product_id=instance.id).delete()
                deleted = True

            if action == 'delete_until_today':
                ProductLocation.objects.filter(product_id=instance.id, created__lt=datetime.date.today()).delete()
                deleted = True
            
            if deleted:
                CommonTool.send_notification(self, self.instance.owner, "locations deleted!", instance.id)

        # OR Update Product
        instance.title = validated_data.get('title', instance.title)
        instance.subtitle = validated_data.get('subtitle', instance.subtitle)
        instance.text = validated_data.get('text', instance.text)
        instance.barcode = validated_data.get('barcode', instance.barcode)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.language = validated_data.get('language', instance.language)
        instance.price = validated_data.get('price', instance.price)
        instance.private = validated_data.get('private', instance.private)
        instance.category = validated_data.get('category', instance.category)


        tags = validated_data.get('tags', None)
        for el in instance.tags.all():
            instance.tags.remove(el)   

        if tags:
            for el in tags:
                instance.tags.add(el)

        locations = validated_data.get('productlocation_set', [])
        
        # For Form POST
        if not locations:
            locations = self.context.get('view').request.POST.get('locations', [])
            if locations:
                try:
                    locations = self.validate_locations(json.loads(locations))
                except:
                    raise serializers.ValidationError('please use this syntax [{"coords": [6.627231, 43.541580]}]')

        for location in locations:
            look_around = settings.LOOK_AROUND
            distance = look_around + 0.1

            existing_locations = ProductLocation.objects.filter(product_id=instance.id)
            # lon/lat
            location = 'POINT(' + str(location['coords'][0]) + ' ' + str(location['coords'][1]) + ')'

            if existing_locations:
                last_location = existing_locations.last().coords

                with connection.cursor() as cursor:
                    last_location_position = 'POINT(' + str(last_location.x) + ' ' + str(last_location.y) + ')'
                    query = "SELECT ST_Distance(geography(ST_GeomFromText('%s',4326)), geography(ST_GeomFromText('%s',4326)), false)" % (last_location_position, location)
                    cursor.execute(query)
                    distance = cursor.fetchone()[0]

            if distance > look_around:
                ProductLocation.objects.create(product_id=instance.id, coords=location)
            else:
                with transaction.atomic():
                    product_to_update = ProductLocation.objects.select_for_update().filter(product_id=instance.id).last()
                    ProductLocation.objects.filter(id=product_to_update.id).update(created=datetime.datetime.now())

        instance.save()

        tmp_highlight = u''
        for key, value in instance.__dict__.items():
             if not key.startswith('_') and key not in ('highlight','search_vector',):
                 tmp_highlight +=  u'<p>%s:%s</p>' % (key, value)

        product_highlight = Product.objects.get(id=instance.id).highlight
        regex = re.compile(r'(<div id="text">)(.*?)(</div><div id="separator"></div>)')
        replaced = regex.sub(r"\1" + tmp_highlight + r"\3", product_highlight, 1)

        Product.objects.filter(id=instance.id).update(highlight=replaced)

        # Update Media
        images_data = {}
        videos_data = {}
        audios_data = {}
        files_data = {}
        tmp_highlight = ''

        CommonTool.set_media_type(self, self.context.get('view').request.FILES.items(), images_data, videos_data, audios_data, files_data)
 
        product = Product.objects.get(id=instance.id)

        if images_data is not None or videos_data is not None or audios_data is not None or files_data is not None:
   
            for image_data in images_data.values():
                stored_image = ProductImage.objects.create(product=product, image=image_data)
                tag_to_add = u'<img src="%s"/>' % stored_image.image.url

                regex = re.compile(r'(.*>)(.*?)(</div><div id="videos">)')
                replaced = regex.sub(r"\1" + tag_to_add + r"\3", product_highlight, 1)
                product_highlight = replaced
                Product.objects.filter(id=instance.id).update(highlight=replaced)

            for video_data in videos_data.values():
                stored_video = ProductVideo.objects.create(product=product, video=video_data)
                tag_to_add = u'<video controls><source src="%s"/></video>' % stored_video.video.url
                
                regex = re.compile(r'(.*>)(.*?)(</div><div id="audios">)')
                replaced = regex.sub(r"\1" + tag_to_add + r"\3", product_highlight, 1)
                product_highlight = replaced
                Product.objects.filter(id=instance.id).update(highlight=replaced)
       
            for audio_data in audios_data.values():
                stored_audio = ProductAudio.objects.create(product=product, audio=audio_data)
                tag_to_add = u'<audio controls><source src="%s"/></audio>' % stored_audio.audio.url

                regex = re.compile(r'(.*>)(.*?)(</div><div id="files">)')
                replaced = regex.sub(r"\1" + tag_to_add + r"\3", product_highlight, 1)
                product_highlight = replaced
                Product.objects.filter(id=instance.id).update(highlight=replaced)

            for file_data in files_data.values():
                stored_file = ProductFile.objects.create(product=product, file=file_data)
                tag_to_add = u'<a href="%s" download><img src="%s" alt="download"></a>' % (stored_file.file.url, CommonTool.download_image)

                regex = re.compile(r'(.*>)(.*?)(</div></div></body>)')
                replaced = regex.sub(r"\1" + tag_to_add + r"\3", product_highlight, 1)
                product_highlight = replaced
                Product.objects.filter(id=instance.id).update(highlight=replaced)

            try:
                CommonTool.send_notification(self, self.instance.owner, instance.title + " updated!", instance.id)
            except:
                pass

        return instance

        
    def create(self, validated_data):

        images_data = {}
        videos_data = {}
        audios_data = {}
        files_data = {}
        tmp_highlight = ''

        CommonTool.set_media_type(self, self.context.get('view').request.FILES.items(), images_data, videos_data, audios_data, files_data)

        tags = []
        try:
            tags = validated_data.pop('tags')
        except:
            pass

        locations = []
        try:
            locations = validated_data.pop('productlocation_set')
        except:
            pass

        # For Form POST
        if not locations:
            locations = self.context.get('view').request.POST.get('locations', [])
            if locations:
                try:
                    locations = self.validate_locations(json.loads(locations))
                except:
                    raise serializers.ValidationError('please use this syntax [{"coords": [6.627231, 43.541580]}]')

        validated_fields_ignored = validated_entries(validated_data,['productimage_set','productvideo_set', 'productaudio_set','productfile_set',''])
        product = eval("Product.objects.create(" + validated_fields_ignored.get_string()[:-1] + ")")

        for el in tags:
            product.tags.add(el)

        for location in locations:
            ProductLocation.objects.create(product=product, coords="POINT(" + str(location['coords'][0]) + " " + str(location['coords'][1]) + ")")

        tmp_highlight += u'<!DOCTYPE html>' \
                         u'<body><div id="text">'
        for key, value in product.__dict__.items():
             if not key.startswith('_') and key not in ('highlight','search_vector'):
                 tmp_highlight +=  u'<p>%s:%s</p>' % (key, value)
        tmp_highlight += u'</div>' \
                         u'<div id="separator"></div>'

        if images_data is not None or videos_data is not None or audios_data is not None or files_data is not None:

            tmp_highlight += u'<div id="media"><div id="images">'     
            for image_data in images_data.values():
                stored_image = ProductImage.objects.create(product=product, image=image_data)
                tmp_highlight += u'<img src="%s"/>' % stored_image.image.url
            tmp_highlight += u'</div>'

            tmp_highlight += u'<div id="videos">'         
            for video_data in videos_data.values():
                stored_video = ProductVideo.objects.create(product=product, video=video_data)
                tmp_highlight += u'<video controls><source src="%s"/></video>' % stored_video.video.url
            tmp_highlight += u'</div>'

            tmp_highlight += u'<div id="audios">'         
            for audio_data in audios_data.values():
                stored_audio = ProductAudio.objects.create(product=product, audio=audio_data)
                tmp_highlight += u'<audio controls><source src="%s"/></audio>' % stored_audio.audio.url
            tmp_highlight += u'</div>'

            tmp_highlight += u'<div id="files">'         
            for file_data in files_data.values():
                stored_file = ProductFile.objects.create(product=product, file=file_data)
                tmp_highlight += u'<a href="%s" download><img src="%s" alt="download"></a>' % (stored_file.file.url, CommonTool.download_image,)
            tmp_highlight += u'</div></div></body></html>'

        Product.objects.filter(id=product.id).update(highlight=tmp_highlight)

        try:
            CommonTool.send_notification(self, product.owner, validated_data['title'] + " created!", product.id)
        except:
            pass

        return product


class GroupSerializerOwner(serializers.ModelSerializer, CommonTool):
    groups = GroupSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('id','username','groups',)
        read_only_fields = ('id','username',)

    def validate_groups(self, value):
        for el in value:
            try:
                user_to_add = User.objects.get(username=el['name'])
                Profile.objects.get(user=user_to_add.id).user_group
            except:
                raise serializers.ValidationError("%s in not a valid username." % el['name'])

        return value

    def update(self, instance, validated_data):
        user = User.objects.get(username=instance.username)

        for group in validated_data['groups']:

            group_to_add = group['name']
            user_to_add = User.objects.get(username=group['name'])
            group_to_add = Profile.objects.get(user=user_to_add.id).user_group


            # Check if user already in group
            if not user.groups.filter(name=group_to_add).exists():

                # Add user to group
                try:
                    request_group = Group.objects.get(name=group_to_add)
                except:
                    GroupAcknowlegment.objects.filter(group_name=group_to_add).delete()
                    raise serializers.ValidationError("User does not exist anymore!")

                if settings.PRIVACY_MODE[0] == 'PRIVATE':
                    request_group.user_set.add(user)

                user_profile = Profile.objects.get(user_group=request_group.name)
                owner = User.objects.get(username=user_profile.user)

                user_group = Profile.objects.get(user=user)

                # Share asker group
                if settings.PRIVACY_MODE[0] == 'PRIVATE':
                    existing_group = Group.objects.get(name=user_group.user_group)
                    existing_group.user_set.add(owner)

                    # Notification
                    try:
                        CommonTool.send_notification(self, user, user.username + " has been added!")
                        CommonTool.send_notification(self, user_to_add, user_to_add.username + " has been added!")
                    except:
                        pass
                else:
                    # PRIVATE-VALIDATION
                    pending_group = GroupAcknowlegment.objects.get_or_create(group_asker=user, group_asker_username=user.username, group_name=request_group.name, group_owner=owner, activate=False)

                    # Notification
                    try:
                        CommonTool.send_notification(self, user, user_to_add.username + " request sent!")
                        CommonTool.send_notification(self, user_to_add, user.username + " request sent!")
                    except:
                        pass

            # Friend has been already added
            else:
                # Notification
                try:
                    CommonTool.send_notification(self, user, user_to_add.username + " already added!")
                except:
                    pass

        if settings.PRIVACY_MODE[0] == 'PRIVATE':
            return user
        else:
            return validated_data



class GroupAcknowlegmentSerializer(serializers.ModelSerializer, CommonTool):
    
    class Meta:
        model = GroupAcknowlegment
        fields = ('id', 'group_asker','group_asker_username','group_name','group_owner','activate',)
        read_only_fields = ('id','group_owner','group_asker','group_name','group_asker_username')

    def update(self, instance, validated_data):

        group_asker = validated_data.get('group_asker', instance.group_asker)
        group_name = validated_data.get('group_name', instance.group_name)
        group_owner = validated_data.get('group_owner', instance.group_owner)

        user_asker = User.objects.get(username=group_asker)

        if validated_data['activate']:

            existing_group = []
            try:
                existing_group = Group.objects.get(name=group_name)
            except:
                GroupAcknowlegment.objects.filter(group_name=group_name).delete()
                group_not_exist = False
                raise serializers.ValidationError("User does not exist anymore!")

            existing_group.user_set.add(user_asker)

            # Share asker group
            user = User.objects.get(username=group_owner)

            asker = User.objects.get(username=group_asker)
            user_group = Profile.objects.get(user=asker)

            existing_group = Group.objects.get(name=user_group.user_group)
            existing_group.user_set.add(user)


            # Notification
            try:
                CommonTool.send_notification(self, user_asker, user.username + " accepted the request!")
                CommonTool.send_notification(self, user, user_asker.username + " request validated!")
            except:
                pass

        GroupAcknowlegment.objects.get(group_asker=group_asker, group_name=group_name).delete()

        # Notification
        if not validated_data['activate']:
            try:
                CommonTool.send_notification(self, user_asker, user.username + " rejected " + user_asker.username + " request!")
            except:
                pass

        instance.activate = validated_data['activate']
        return instance



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ('user',)

class ProfileImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    profile = ProfileSerializer()

    tags = serializers.SerializerMethodField(required=False)
    categories = serializers.SerializerMethodField(required=False)

    products = serializers.SerializerMethodField(required=False)

    def get_products(self, obj):
        # Get Total
        return Product.objects.filter(owner=obj.profile.user).count()

    def get_tags(self, obj):
        # Get Number of Tags
        return Product.objects.filter(owner=obj.profile.user).values('tags__name').annotate(total=Count('tags__name')).order_by('-total')

    def get_categories(self, obj):
        # Get Number of Categories
        return Product.objects.filter(owner=obj.profile.user).values('category__name').annotate(total=Count('category__name')).order_by('-total')

    class Meta:
        model = ProfileImage
        fields = ('id','image','profile','tags','categories','products')
        read_only_fields = ('profile','tags','categories','products')
        


class CategorySerializer(serializers.ModelSerializer):
    are_children_started = serializers.SerializerMethodField()

    def get_are_children_started(self, obj):
        return all(category.started for category in Category.get_tree(obj))

    class Meta:
        model = Category
        fields = ('__all__')
        read_only_fields = ('name','slug',)


class TagsSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return all(Tag.objects.all())

    class Meta:
        model = Tag
        fields = ('__all__')
        read_only_fields = ('name','slug',)