# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-26 03:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0221_auto_20210225_1511'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionoption',
            old_name='name',
            new_name='label',
        ),
        migrations.AddField(
            model_name='questionoption',
            name='value',
            field=models.CharField(default='yes', max_length=100),
            preserve_default=False,
        ),
    ]