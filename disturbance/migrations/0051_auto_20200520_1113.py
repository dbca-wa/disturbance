# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-05-20 03:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0050_merge_20200520_0753'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProposalApiarySiteLocation',
            new_name='ProposalApiary',
        ),
    ]
