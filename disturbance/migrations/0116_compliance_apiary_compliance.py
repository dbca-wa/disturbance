# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-07-24 08:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0115_merge_20200723_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliance',
            name='apiary_compliance',
            field=models.BooleanField(default=False),
        ),
    ]
