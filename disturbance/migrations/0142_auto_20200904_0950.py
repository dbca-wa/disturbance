# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-09-04 01:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0141_proposalapiary_vacant_apiary_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalapiary',
            name='vacant_apiary_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='proposal_apiaries', to='disturbance.ApiarySite'),
        ),
    ]
