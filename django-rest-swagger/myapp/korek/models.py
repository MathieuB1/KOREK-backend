import os
from django.contrib.gis.db import models
from django.contrib.auth.models import User

from unidecode import unidecode

from PIL import Image, ExifTags
import base64

from django.core.files import File

# Tags
from taggit.managers import TaggableManager

# Category
from treebeard.mp_tree import MP_Node
from django.template.defaultfilters import slugify

# Full text search
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

# Signals
from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.cache import cache

class Category(MP_Node):
    name = models.CharField(max_length=50)
    started = models.BooleanField(default=True)
    node_order_by = ['name']
    slug = models.SlugField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return 'Category: %s' % self.name


class Product(models.Model):
    # Attributes Class
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    title = models.CharField(max_length=100, blank=False, db_index=True)
    subtitle = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=True, max_length=10000)
    barcode = models.IntegerField(blank=True, default=0, db_index=True)
    brand = models.TextField(blank=True)
    language = models.CharField(default='fr', max_length=3)
    price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True, null=True)
    owner = models.ForeignKey('auth.User', related_name='products', on_delete=models.CASCADE, db_index=True)
    highlight = models.TextField()
    date_uploaded = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    tags = TaggableManager(blank=True)

    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ('created',)
        indexes = [GinIndex(fields=['search_vector']),
                   models.Index(fields=['owner', 'private'],name='product_ownerprivate_idx'),]
        

    def save(self, *args, **kwargs):
        # Create and save the validated object
        super(Product, self).save(*args, **kwargs)


@receiver(post_save, sender=Product)
def update_search_vector(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.pk).update(search_vector=SearchVector('title','subtitle','text'))


class ProductLocation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    coords = models.PointField(blank=True, null=True)

    class Meta:
        ordering = ('created',)
        indexes = [ models.Index(fields=['product', 'created'],name='location_productcreated_idx'), ]

def user_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Products_Image/{0}/{1}'.format(instance.product.owner.id, unidecode(filename))


def autoRotateImage(_image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(_image._getexif().items())

        if exif[orientation] == 3:
            _image = _image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            _image = _image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            _image = _image.rotate(90, expand=True)
        return _image
    except:
        return _image



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(blank=True, upload_to=user_image_path, default="")

    def save(self, *args, **kwargs):
        if not self.image:
            return

        super(ProductImage, self).save(*args, **kwargs)

        try:
            filename = self.image.path
            pilImage = Image.open(filename)

            pilImage = autoRotateImage(pilImage)

            pilImage.save(filename)
            pilImage.close()
        except:
            pass


def user_video_path(instance, filename):
    return 'Products_Video/{0}/{1}'.format(instance.product.owner.id, unidecode(filename))

class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    video = models.FileField(blank=True, upload_to=user_video_path, default="")

def user_audio_path(instance, filename):
    return 'Products_Audio/{0}/{1}'.format(instance.product.owner.id, unidecode(filename))

class ProductAudio(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    audio = models.FileField(blank=True, upload_to=user_audio_path, default="")

def user_file_path(instance, filename):
    return 'Products_File/{0}/{1}'.format(instance.product.owner.id, unidecode(filename))

class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    file = models.FileField(blank=True, upload_to=user_file_path, default="")

class Profile(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    user_group = models.TextField(max_length=80, blank=True, db_index=True)


def user_profile_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Profile_Image/{0}/{1}'.format(instance.profile.id, unidecode(filename))

class ProfileImage(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, db_index=True)
    _image = models.ImageField(blank=True, upload_to=user_profile_path, default="anonymous.png")

    def save(self, *args, **kwargs):
        """
        Save Photo after ensuring it is not blank.  Resize as needed.
        """
        if not self._image:
            return

        super(ProfileImage, self).save(*args, **kwargs)

        filename = self._image.path
        _image = Image.open(filename)
        _image.thumbnail((50, 50), Image.ANTIALIAS)

        _image = autoRotateImage(_image)

        _image.save(filename)
        _image.close()

    @property
    def image(self):
        if cache.get(self._image.path):
            return cache.get(self._image.path)
        else:
            try:
                img = open(self._image.path, "rb")
                data = base64.b64encode(img.read())
                cache.set(self._image.path, "data:image/jpg;base64,%s" % data.decode("utf-8"), timeout=3600) 
                return "data:image/jpg;base64,%s" % data.decode("utf-8")
            except IOError:
                return self._image.url

    @image.setter
    def image(self, value):
        self._image = value


class GroupAcknowlegment(models.Model):
    group_asker = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    group_asker_username = models.TextField(blank=True, default="", db_index=True)
    group_name = models.TextField(blank=True, max_length=80, default="", db_index=True)
    group_owner = models.TextField(blank=True, default="", db_index=True)
    activate = models.BooleanField(default=False)


class PasswordReset(models.Model):
    user_email = models.EmailField(blank=False, db_index=True)
    tmp_url = models.TextField(blank=True, default="")
    password = models.TextField(blank=False)


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    comment = models.TextField(blank=False,  max_length=250)

    class Meta:
        ordering = ('created',)
        indexes = [ models.Index(fields=['product', 'created'],name='comment_productcreated_idx'), ]
