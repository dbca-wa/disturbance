# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-07-02 03:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0096_auto_20200702_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annualrentalfee',
            name='payment_type',
        ),
    ]
