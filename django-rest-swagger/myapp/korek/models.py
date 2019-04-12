from django.db import models
from django.contrib.auth.models import User

from PIL import Image
from django.utils.encoding import smart_str
from django.utils import encoding

import base64



class Product(models.Model):
    # Attributes Class
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    title = models.CharField(max_length=100, blank=False, db_index=True)
    subtitle = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=False, max_length=1000)
    barcode = models.IntegerField(blank=True, default=0, db_index=True)
    brand = models.TextField(blank=True)
    language = models.CharField(default='fr', max_length=3)
    lat = models.TextField(blank=True)
    lon = models.TextField(blank=True)
    owner = models.ForeignKey('auth.User', related_name='products', on_delete=models.CASCADE)
    highlight = models.TextField()
    date_uploaded = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ('created',)


    def save(self, *args, **kwargs):
        # Create and save the validated object
        super(Product, self).save(*args, **kwargs)

# Bacause this one can only accepts 2 argument
def user_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Products_Image/{0}/{1}'.format(instance.product.owner.id, filename)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(blank=True, upload_to=user_image_path, default="")
                
    class Meta:
        unique_together = ('product', 'image')

def user_video_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Products_Video/{0}/{1}'.format(instance.product.owner.id, filename)
    
class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    video = models.FileField(blank=True, upload_to=user_video_path, default="")

    class Meta:
        unique_together = ('product', 'video')

def user_audio_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Products_Audio/{0}/{1}'.format(instance.product.owner.id, filename)

class ProductAudio(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    audio = models.FileField(blank=True, upload_to=user_audio_path, default="")

    class Meta:
        unique_together = ('product', 'audio')



class Profile(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    user_group = models.TextField(max_length=80, blank=True, db_index=True)

def user_profile_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Profile_Image/{0}/{1}'.format(instance.profile.id, filename)

class ProfileImage(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, db_index=True)
    _image = models.ImageField(blank=True, upload_to=user_profile_path, default="")

    class Meta:
        unique_together = ('profile', '_image')

    def save(self, *args, **kwargs):
        """
        Save Photo after ensuring it is not blank.  Resize as needed.
        """
        if not self._image:
            return

        self._image.name = encoding.smart_str(self._image.name, encoding='ascii', errors='ignore')

        # Generate a ramdom image name
        if self._image.name.split(".")[0] == '':
            self._image.name = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(6)) + '.' + self._image.name.split(".")[1]

        super(ProfileImage, self).save(*args, **kwargs)

        filename = self._image.path
        _image = Image.open(filename)
        _image.thumbnail((50, 50), Image.ANTIALIAS)
        _image.save(filename)
		
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

    class Meta:
        unique_together = (('group_owner', 'group_asker'),)


class PasswordReset(models.Model):
    user_email = models.EmailField(blank=False, db_index=True)
    tmp_url = models.TextField(blank=True, default="")
    password = models.TextField(blank=False)