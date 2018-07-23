from django.db import models


class Product(models.Model):
    # Attributes Class
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False, db_index=True)
    subtitle = models.CharField(max_length=100, blank=True)
    text = models.TextField(blank=False, max_length=1000)
    barcode = models.IntegerField(blank=False, db_index=True)
    brand = models.TextField(blank=False)
    language = models.CharField(default='fr', max_length=2)
    owner = models.ForeignKey('auth.User', related_name='products', on_delete=models.CASCADE, db_index=True)
    highlighted = models.TextField()

    class Meta:
        ordering = ('created',)


    def save(self, *args, **kwargs):
        # Create and save the validated object
        super(Product, self).save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(blank=True, upload_to="Products_Image/", default="")

    class Meta:
        unique_together = ('product', 'image')
