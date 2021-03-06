# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-10-05 08:35
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0185_merge_20201005_1601'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaCoast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wkb_geometry', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326)),
                ('type', models.CharField(blank=True, max_length=30, null=True)),
                ('source', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
