# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-05-01 21:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_phrases', models.CharField(max_length=100)),
                ('sentiment', models.CharField(max_length=100)),
                ('confidence_score', models.CharField(max_length=100)),
                ('emotion_detection', models.CharField(max_length=100)),
            ],
        ),
    ]
