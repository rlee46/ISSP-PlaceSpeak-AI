# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import math
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

def count_csv_rows(csv_data):
    # Assuming csv_data is a string containing CSV data
    # Split the CSV data into lines
    lines = csv_data.strip().split('\n')
    
    # Create a new list containing only non-empty lines
    non_empty_lines = [line for line in lines if len(line) > 0]
    
    # Return the count of non-empty data rows
    return len(non_empty_lines)

#estimate number of tokens in the payload
def num_tokens(data):
    pattern = r'\w+|[^\w\s]'
    tokens = re.findall(pattern, data)
    return len(tokens)

def generate_completion(query):
        API_KEY = os.getenv("OPENAI_API_KEY")
        if not API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")

        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer {api_key}".format(api_key=API_KEY),
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
        
        response = requests.post(api_url, headers=headers, json=query_data)
        
        return response

def process_batch(batch_data):
        resultCount = 0
        result = ""
        batch_data_str = str(batch_data)
        row_count = len(batch_data)
        print("batch count: ", row_count)
        while(resultCount != row_count):
        # Construct the query
            query = """
            Generate the result in csv format without any explanation. Do not include a header for the data. For each response,
            column 1: Select one or more keywords from the response. If there is more than one keyword, separate them with `&` not commas
            column 2: Evaluate the sentiment of the response from positive, neutral, or negative
            column 3: Determine the reaction/emotion
            column 4: Generate a confidence score in a percentage
            column 5:Determine the location of the response from csv data
            Format the data as Key Words, Sentiment, Reaction/Emotion, Confidence Score, Location
            Here is an example: `Freedom & Responsibility, Positive, Happy, 100%, City of Burnaby
            Note: The last number is the rows. Return the same number of rows in response`
            """ + batch_data_str + " ROWS: " + str(row_count)   # Concatenate batch_data_str
            result =  generate_completion(query).json().get("choices")[0].get("message").get("content")
            resultCount = count_csv_rows(result)
            if resultCount !=row_count: 
                    print("RERUNNING: Incorrect number of ROWS")
        
        return result

def csv_to_array(csv_data):
    # Split CSV data into lines
    lines = csv_data.strip().split('\n')

    # Get header and remove it from lines
    header = lines.pop(0)
    
    # Split header into keys
    keys = header.split(',')

    # Initialize an empty array to store dictionaries
    data_array = []

    # Iterate over remaining lines to create dictionaries
    for line in lines:
        # Split line into values
        values = line.split(',')
        # Check if the number of values matches the number of keys
        # Skip lines that don't have the correct number of values
        data_dict = {}
        for i, key in enumerate(keys):
            data_dict[key] = values[i].strip()  # Strip any extra whitespace

        data_array.append(data_dict)

    return data_array


def prompt(query_type, data):
    
    # Prepare data to send to the OpenAI API
    if query_type == 'summary':
        query = '''
        I am a government  official who is looking to make a decision based on the input of my community. 
        The following data is sourced from a discussion post where members of my community discussed their views on the topic.
        Please generate a 5 to 10 sentence summary that I can use to communicate their feelings to my colleagues and other policy makers.
        In three sentences or less, please provide a recommendation for how I should proceed based on the feedback observed in this post.   
        Do not format it in markdown, only use plain text.
        ''' + data
        
        return generate_completion(query)
    elif query_type == 'table':
        count = 0
        batch_size = 5
        
        data_array = csv_to_array(data)
        
        num_rows = len(data_array)
        num_batches = math.ceil(num_rows / batch_size)
        
        results = []
        for i in range(int(num_batches+1)):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, num_rows)
            batch_data = data_array[start_idx:end_idx]
            if(len(batch_data) == 0):
                break
            print("----------------------------")
            print("Batch Number: "+ str(i))
            batch_result = process_batch(batch_data)
            print(batch_result)
            row_result = count_csv_rows(batch_result)
            print("result row:", row_result)
            print("----------------------------")
            count += row_result
            results.append(batch_result)
    
    print("Total Lines: " + str(count))
    return results

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
        entries = []
        result = prompt('table', csv_data)
        # Send the request to the OpenAI API
        
        for i in range(len(result)):
        
        # Parse the response data into an array of objects where each object is one row in the table
            
            for line in result[i].strip().split("\n"):
                parts = line.split(',')
                try:
                    entry = {
                        'KeyPhrases': parts[0].strip(),
                        'Sentiment': parts[1].strip(),
                        'ReactionEmotion': parts[2].strip(),
                        'ConfidenceScore': parts[3].strip(),
                        'Location': parts[4].strip()  # New column for location
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
            print("table_prompt done")
            successful_query = True
            
        return entries
        

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
    print("summary done")
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






