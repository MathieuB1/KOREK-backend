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
    text = models.TextField(blank=False, max_length=10000)
    barcode = models.IntegerField(blank=True, default=0, db_index=True)
    brand = models.TextField(blank=True)
    language = models.CharField(default='fr', max_length=3)
    price = models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True, null=True)
    owner = models.ForeignKey('auth.User', related_name='products', on_delete=models.CASCADE)
    highlight = models.TextField()
    date_uploaded = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=False, db_index=True)
    category = models.ManyToManyField(Category, blank=True)
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ('created',)


    def save(self, *args, **kwargs):
        # Create and save the validated object
        super(Product, self).save(*args, **kwargs)


class ProductLocation(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    coords = models.PointField(blank=True, null=True)


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
        try:
            img = open(self._image.path, "rb") 
            data = base64.b64encode(img.read())
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
    group_owner = models.TextField(blank=True, default="")
    activate = models.BooleanField(default=False)


class PasswordReset(models.Model):
    user_email = models.EmailField(blank=False, db_index=True)
    tmp_url = models.TextField(blank=True, default="")
    password = models.TextField(blank=False)


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    comment = models.TextField(blank=False,  max_length=250)