# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

class Report(models.Model):
    key_phrases = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=100)
    confidence_score = models.CharField(max_length=100)
    emotion_detection = models.CharField(max_length=100)

    def __str__(self):
        # Adjusted to use an existing field or a summary
        return "{} - {}".format(self.sentiment,self.emotion_detection)