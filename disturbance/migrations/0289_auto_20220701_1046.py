# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-07-01 02:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0288_auto_20220628_1240'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='districtdbca',
            options={'ordering': ['object_id'], 'verbose_name_plural': 'Apiary DBCA Districts'},
        ),
        migrations.AlterModelOptions(
            name='regiondbca',
            options={'ordering': ['object_id'], 'verbose_name_plural': 'Apiary DBCA Regions'},
        ),
        migrations.AddField(
            model_name='districtdbca',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='regiondbca',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='apiaryglobalsettings',
            name='key',
            field=models.CharField(choices=[('oracle_code_apiary_site_annural_rental_fee', 'Oracle code for the apiary site annual site fee'), ('apiary_sites_list_token', 'Token to import the apiary sites list'), ('apiary_licence_template_file', 'Apiary licence template file'), ('print_deed_poll_url', 'URL of the deed poll'), ('dbca_districts_file', 'DBCA districts geojson file'), ('dbca_regions_file', 'DBCA regions geojson file')], max_length=255, unique=True),
        ),
    ]