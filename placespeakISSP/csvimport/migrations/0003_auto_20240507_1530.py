# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csvimport', '0002_auto_20240507_1517'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_phrases', models.TextField()),
                ('sentiment', models.CharField(max_length=50)),
                ('reaction_emotion', models.CharField(max_length=50)),
                ('confidence_score', models.CharField(max_length=10)),
                ('location', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='analysisdata',
            name='entries',
        ),
        migrations.DeleteModel(
            name='AnalysisData',
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
    ]
