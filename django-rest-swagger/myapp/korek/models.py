from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    # Attributes Class
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False, db_index=True)
    subtitle = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=False, max_length=1000)
    barcode = models.IntegerField(blank=False, db_index=True)
    brand = models.TextField(blank=False)
    language = models.CharField(default='fr', max_length=3)
    owner = models.ForeignKey('auth.User', related_name='products', on_delete=models.CASCADE, db_index=True)
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

# Bacause this one can only accepts 2 argument
def user_video_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Products_Video/{0}/{1}'.format(instance.product.owner.id, filename)
    
class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    video = models.FileField(blank=True, upload_to=user_video_path, default="")

    class Meta:
        unique_together = ('product', 'video')


class Profile(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    user_group = models.TextField(max_length=80, blank=True, db_index=True)


class GroupAcknowlegment(models.Model):
    group_asker = models.ForeignKey('auth.User', on_delete=models.CASCADE, db_index=True)
    group_name = models.TextField(blank=True, max_length=80, default="")
    group_owner = models.TextField(blank=True, default="")
    activate = models.BooleanField(default=False)

    class Meta:
        unique_together = (('group_owner', 'group_asker'),)


class PasswordReset(models.Model):
    user_email = models.EmailField(blank=False)
    tmp_url = models.TextField(blank=True, default="")
    password = models.TextField(blank=False)