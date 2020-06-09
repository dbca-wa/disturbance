# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-06-08 13:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0069_auto_20200608_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temporaryuseapiarysite',
            name='apiary_site_approval',
        ),
        migrations.AddField(
            model_name='temporaryuseapiarysite',
            name='apiary_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='disturbance.ApiarySite'),
        ),
        migrations.AlterField(
            model_name='temporaryuseapiarysite',
            name='proposal_apiary_temporary_use',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='disturbance.ProposalApiaryTemporaryUse'),
        ),
    ]