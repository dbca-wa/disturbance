# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-25 03:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0233_auto_20210325_1055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='masterlistquestion',
            old_name='help_tex',
            new_name='help_text',
        ),
        migrations.RenameField(
            model_name='masterlistquestion',
            old_name='help_tex_assessor',
            new_name='help_text_assessor',
        ),
    ]
