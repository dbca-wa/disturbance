# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-05-19 23:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0048_auto_20200519_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalapiarytemporaryuse',
            name='proposal_apiary_base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='apiary_temporary_use_set', to='disturbance.Proposal'),
        ),
        migrations.AlterField(
            model_name='proposalapiarytemporaryuse',
            name='proposal',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='apiary_temporary_use', to='disturbance.Proposal'),
        ),
    ]
