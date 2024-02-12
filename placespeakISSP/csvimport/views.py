# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import random
from random import choice, randint
from datetime import datetime,timedelta

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def generate_example_report():
    
    sentiments = ['Positive', 'Negative', 'Neutral']
    emotions = ['Joy', 'Anger', 'Surprise', 'Sadness', 'Fear']
    start_date = datetime(2012, 1, 1)
    end_date = datetime.now()

    # Generate dummy data
    data = []
    for i in range(1, 11):  # Let's generate 10 entries for example
        entry = {
            'id': i,
            'generation_date': random_date(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S"),
            'title': "Post Title {}".format(i),
            'key_phrases': "Phrase {}, Phrase {}".format(random.randint(1, 5), random.randint(6, 10)),
            'sentiment': random.choice(sentiments),
            'confidence_score': "{}.{}%".format(random.randint(90, 99), random.randint(10, 99)),
            'emotion_detection': random.choice(emotions),
        }
        data.append(entry)
    return data


def home(request):
    entries = generate_example_report()

    return render(request, 'report.html', {'entries': entries})