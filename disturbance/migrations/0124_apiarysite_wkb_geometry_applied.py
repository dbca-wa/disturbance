# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-10 02:10
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0123_auto_20200805_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiarysite',
            name='wkb_geometry_applied',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
