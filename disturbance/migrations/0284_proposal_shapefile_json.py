# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-01-25 13:20
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0283_merge_20220121_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='shapefile_json',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]