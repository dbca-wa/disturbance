# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-10-27 03:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0189_proposalapiary_transferee_email_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiarysiteonproposal',
            name='application_fee_paid',
            field=models.BooleanField(default=False),
        ),
    ]
