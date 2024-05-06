# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render,redirect

from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from . serializer import *
from django.http import QueryDict

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from tests.test_confidence import test_confidence
from tests.test_sentiment import test_sentiment
from collections import defaultdict
import requests
import csv
import re
import time
import json

class CSVAnalysisView(APIView):
    def post(self, request):
        # Parse the form-encoded data
        form_data = QueryDict(request.body)
        json_string = form_data.get('_content')

        if not json_string:
            return Response({'error': 'Missing JSON data'}, status=400)

        try:
            # Decode and load JSON data
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            return Response({'error': 'Invalid JSON: ' + str(e)}, status=400)

        # Use the serializer to validate the data
        serializer = CSVUploadSerializer(data=data)
        if serializer.is_valid():
            csv_data = serializer.validated_data['csv_data']
            # Process the CSV data here and return analysis
            return generate_analysis(csv_data)
        else:
            return Response(serializer.errors, status=400)

def remove_non_printable_chars(text):
    # Define the pattern to match only printable characters
    printable_pattern = re.compile(r'[^\x20-\x7E]')
    # Substitute non-printable characters with an empty string
    clean_text = re.sub(printable_pattern, '', text)
    return clean_text

def prompt(query_type, data):
    API_KEY = os.getenv("OPENAI_API_KEY")
    print(API_KEY)
    if not API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    # Prepare data to send to the OpenAI API
    if query_type == 'summary':
        query = '''
        I am a government  official who is looking to make a decision based on the input of my community. 
        The following data is sourced from a discussion post where members of my community discussed their views on the topic.
        Please generate a 5 to 10 sentence summary that I can use to communicate their feelings to my colleagues and other policy makers.
        In three sentences or less, please provide a recommendation for how I should proceed based on the feedback observed in this post.   
        Do not format it in markdown, only use plain text.
        ''' + data
    elif query_type == 'table':
        query = """
        Generate the result in csv format without any explaination. Do not include a header for the data. For each response,
        column 1:Select one or more key words from the response. If there is more than one key word, seperate them with `&` not commas
        column 2:Evaluate the sentiment of the response from positive, neutral, or negative
        column 3:Determine the reaction/emotion
        column 4:Generate a confidence score in a percentage  
        Format the data as Key Words, Sentiment, Reaction/Emotion, Confidence Score
        Here is an example: `Freedom & Responsibility, Positive, Happy, 100%`
        """ + data
    
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer {api_key}".format(api_key = API_KEY),  # API key
        "Content-Type": "application/json",
    }
    query_data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ],
    "max_tokens": 4096,
    }

    return requests.post(api_url, headers=headers, json=query_data)

def summary_prompt(csv_data):
    response = prompt('summary', csv_data)
    if response.status_code == 200:
        summary_data = response.json()
        return summary_data.get("choices")[0].get("message").get("content")
    else:
        return JsonResponse({'error': response.text}, status=response.status_code)
        
def table_prompt(csv_data):
    # Loops the prompt untill the returned values pass the data tests
    successful_query = False
    while not successful_query:

        # Send the request to the OpenAI API
        response = prompt('table', csv_data)
        if response.status_code == 200:
            response_data = response.json()
            result = response_data.get("choices")[0].get("message").get("content")
            # Parse the response data into an array of objects where each object is one row in the table
            entries = []
            for line in result.strip().split("\n"):
                parts = line.split(',')
                # Create a dictionary for each line and append to entries
                try:
                    entry = {
                        'KeyPhrases': parts[0].strip(),
                        'Sentiment': parts[1].strip(),
                        'ReactionEmotion': parts[2].strip(),
                        'ConfidenceScore': parts[3].strip(),
                    }
                    entries.append(entry)
                except:
                    break

            # Test data to see if resembles our expectations  
            # Test confidence scores ensures that the value associated with the confidence score attribute is an integer between 0 and 100
            # Test sentiment ensures that the value associated with the sentiment attribute is one of ['Positive', 'Neutral', 'Negative'] 
            # Should either of these tests fail, the prompt is rerun after a short delay    
            if not(test_confidence(entries) or test_sentiment(entries)):
                time.sleep(5)
                continue
            else:
                print(entries)
                successful_query = True
            
            return entries
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

def calculate_sentiment_frequencies(entries):
    sentiment_counts = defaultdict(int)
    for entry in entries:
        sentiment = entry.get('Sentiment', '').capitalize()
        if sentiment in ['Neutral', 'Positive', 'Negative']:
            sentiment_counts[sentiment] += 1
    return dict(sentiment_counts)

def calculate_frequencies(entries):
    # Convert confidence scores to integers and bin them
    bins = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']
    score_bins = {bin: 0 for bin in bins}
    
    for entry in entries:
        score = int(entry['ConfidenceScore'].rstrip('%'))
        bin_index = min(score // 10, 9)  # to put 100% in the '90-100' bin
        bin_label = bins[bin_index]
        score_bins[bin_label] += 1

    return [score_bins[bin] for bin in bins]

def generate_analysis(csv_data):
    # Generate and execute the prompt to create the summary and table
    summary_data = summary_prompt(csv_data)
    table_data = table_prompt(csv_data)

    # Calculate confidence scores
    confidence_frequencies = calculate_frequencies(table_data)
    sentiment_frequencies = calculate_sentiment_frequencies(table_data)

    # Prepare data for serialization
    analysis_data = {
        "summary": summary_data,
        "entries": table_data,
        "confidence_frequencies": confidence_frequencies,
        "sentiment_frequencies": sentiment_frequencies
    }

    # Use the serializer to validate and format the response data
    serializer = AnalysisDataSerializer(data=analysis_data)
    if serializer.is_valid():
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)






