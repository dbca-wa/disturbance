# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-05 03:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0122_auto_20200805_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiarychecklistquestion',
            name='checklist_role',
            field=models.CharField(choices=[('assessor', 'Assessor'), ('applicant', 'Applicant'), ('referrer', 'Referrer')], default='applicant', max_length=30, verbose_name='Checklist Role'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='apiarychecklistquestion',
            name='answer_type',
            field=models.CharField(choices=[('yes_no', 'Yes/No type'), ('free_text', 'Free text type')], default='yes_no', max_length=30, verbose_name='Answer Type'),
        ),
    ]
