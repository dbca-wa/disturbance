# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-08-12 06:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0255_auto_20210805_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionquestion',
            name='property_cache',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True),
        ),
    ]
