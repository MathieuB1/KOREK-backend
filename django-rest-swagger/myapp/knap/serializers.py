from rest_framework import serializers
from knap.models import Product, ProductImage
from django.contrib.auth.models import User


class validated_entries(object):
    val = ""
    def __init__(self, initial_data):
        for key in initial_data:
            # Ignore some Fields
            if key != 'productimage_set':
                self.val += key + "=validated_data.get('" + key + "'),"
    def get_string(self):
            return self.val


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, max_length=None, use_url=True,  style={'autofocus': True, 'placeholder': ''})

    class Meta:
        model = ProductImage
        fields = ('image',)


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    images = ProductImageSerializer(source='productimage_set', required=False, many=True)
    barcode =  serializers.IntegerField(required=True, style={'hide_label': False, 'placeholder': '0'})


    highlight = serializers.HyperlinkedIdentityField(
                  view_name='product-highlight', format='html')
    class Meta:
        model = Product
        fields = ('url','id', 'created', 'highlight', 'title', 'subtitle', 'text', 'barcode', 'brand', 'owner','language','images',)


    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        
        validated_fields = validated_entries(validated_data)
        product = eval("Product.objects.create(" + validated_fields.get_string()[:-1] + ")")
        
        for image_data in images_data.values():
            ProductImage.objects.create(product=product, image=image_data)
        return product

class UserSerializer(serializers.HyperlinkedModelSerializer):
    products = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='product-detail', many=True)

    class Meta:
        model = User
        fields = ('url','id', 'username','products',)


