# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-11-09 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0202_auto_20201109_1004'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportingapplicationdocument',
            name='can_delete',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='supportingapplicationdocument',
            name='input_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='supportingapplicationdocument',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
