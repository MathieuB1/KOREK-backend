# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('korek', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='Product',
            name='language',
            field=models.TextField(choices=[('fr', 'FR'),('en', 'EN')], default='fr', max_length=3),
        ),
    ]
