# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-09-22 03:53
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0167_auto_20200922_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigratedApiaryLicences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permit_number', models.IntegerField()),
                ('start_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('issue_date', models.DateField()),
                ('status', models.CharField(choices=[('current', 'Current'), ('expired', 'Expired'), ('cancelled', 'Cancelled'), ('surrendered', 'Surrendered'), ('suspended', 'Suspended')], default='current', max_length=40)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('trading_name', models.CharField(blank=True, max_length=256, null=True)),
                ('licencee', models.CharField(blank=True, max_length=256, null=True)),
                ('abn', models.CharField(blank=True, max_length=50, null=True, verbose_name='ABN')),
                ('first_name', models.CharField(max_length=128, verbose_name='Given name(s)')),
                ('last_name', models.CharField(max_length=128)),
                ('address_line1', models.CharField(max_length=255, verbose_name='Line 1')),
                ('address_line2', models.CharField(blank=True, max_length=255, verbose_name='Line 2')),
                ('address_line3', models.CharField(blank=True, max_length=255, verbose_name='Line 3')),
                ('suburb', models.CharField(max_length=255, verbose_name='Suburb / Town')),
                ('state', models.CharField(blank=True, default='WA', max_length=255)),
                ('country', django_countries.fields.CountryField(default='AU', max_length=2)),
                ('postcode', models.CharField(max_length=10)),
                ('phone_number1', models.CharField(blank=True, max_length=50, null=True, verbose_name='phone number')),
                ('phone_number2', models.CharField(blank=True, max_length=50, null=True, verbose_name='phone number')),
                ('mobile_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='mobile number')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
    ]