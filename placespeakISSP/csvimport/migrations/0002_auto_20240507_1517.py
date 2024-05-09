# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csvimport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summary', models.TextField(blank=True)),
                ('confidence_frequencies', models.TextField()),
                ('sentiment_frequencies', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CSVUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('csv_data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_phrases', models.CharField(max_length=255)),
                ('sentiment', models.CharField(max_length=50)),
                ('reaction_emotion', models.CharField(max_length=50)),
                ('confidence_score', models.CharField(max_length=10)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
        migrations.DeleteModel(
            name='Report',
        ),
        migrations.AddField(
            model_name='analysisdata',
            name='entries',
            field=models.ManyToManyField(to='csvimport.Entry'),
        ),
    ]
