# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-05 06:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0123_auto_20200805_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiarychecklistanswer',
            name='text_answer',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
