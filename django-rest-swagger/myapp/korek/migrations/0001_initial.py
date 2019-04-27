# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-09 18:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('title', models.CharField(blank=False, max_length=100, db_index=True)),
                ('subtitle', models.CharField(blank=True, max_length=100)),
                ('text', models.TextField(blank=False, max_length=10000)),
                ('barcode', models.IntegerField(blank=True, default=0, db_index=True)),
                ('brand', models.CharField(blank=True, max_length=100)),
                ('language', models.CharField(default='fr', max_length=2)),
                ('highlight', models.TextField()),
                ('price', models.DecimalField(default=0.00, max_digits=20, decimal_places=2, blank=True, null=True)),
                ('lat', models.TextField()),
                ('lon', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL)),
                ('date_uploaded', models.DateTimeField(auto_now=True)),
                ('private', models.BooleanField(default=False, db_index=True))
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_image', to='korek.Product')),
                ('image', models.ImageField(blank=True, upload_to="Products_Image/", default="")),
           ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='ProductVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_video', to='korek.Product')),
                ('video', models.FileField(blank=True, upload_to="Products_Video/", default="")),
           ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='ProductAudio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_audio', to='korek.Product')),
                ('audio', models.FileField(blank=True, upload_to="Products_Audio/", default="")),
           ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='GroupAcknowlegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_asker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_acknowlegment', to=settings.AUTH_USER_MODEL)),
                ('group_asker_username', models.TextField(blank=True, default="", db_index=True)),
                ('group_name', models.TextField(blank=True, max_length=80, default="", db_index=True)),
                ('group_owner', models.TextField(blank=True, default="")),
                ('activate', models.BooleanField(default=False)),
           ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_group', models.TextField(max_length=80, blank=True, db_index=True)),
           ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='ProfileImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile_image', to='korek.Profile')),
                ('_image', models.FileField(blank=True, upload_to="Profile_Image/", default="anonymous.png")),
           ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.EmailField(blank=False, db_index=True)),
                ('tmp_url', models.TextField(blank=True, default="")),
                ('password', models.TextField(blank=False)),
           ],
        ),
    ]
