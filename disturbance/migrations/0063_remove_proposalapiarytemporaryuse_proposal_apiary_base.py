# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-06-05 05:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0062_merge_20200529_1021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposalapiarytemporaryuse',
            name='proposal_apiary_base',
        ),
    ]
