# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-11-16 10:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0278_auto_20211110_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='migratedapiarylicence',
            name='permit_number',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
