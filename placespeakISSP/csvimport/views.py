# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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

class ReportView(APIView):
    def get(self, request):
        report = Report.objects.all()
        serializer = ReportSerializer(report, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReportSerializer(data=request.data)  # Deserialize data from request
        if serializer.is_valid(raise_exception=True):
            serializer.save()  # Save new Report object to database
            return Response(serializer.data)  
        return Response(serializer.errors)

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

        csv_data = data.get('csv_data')
        if not csv_data:
            return Response({"error": "CSV data is required"}, status=400)

        # Assume you process CSV data here and return analysis
        return generate_analysis(csv_data)

def remove_non_printable_chars(text):
    # Define the pattern to match only printable characters
    printable_pattern = re.compile(r'[^\x20-\x7E]')
    # Substitute non-printable characters with an empty string
    clean_text = re.sub(printable_pattern, '', text)
    return clean_text

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
        "Authorization": "Bearer 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",  # API key
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

# def summary_prompt(request):
#     response = prompt('summary', request.session.get('csv_data'))
#     if response.status_code == 200:
#         summary_data = response.json()
#         request.session['summary'] = summary_data.get("choices")[0].get("message").get("content")
#     else:
#         return JsonResponse({'error': response.text}, status=response.status_code)

def summary_prompt(csv_data):
    response = prompt('summary', csv_data)
    if response.status_code == 200:
        summary_data = response.json()
        return summary_data.get("choices")[0].get("message").get("content")
    else:
        return JsonResponse({'error': response.text}, status=response.status_code)

# def table_prompt(request):
#     # Loops the prompt untill the returned values pass the data tests
#     successful_query = False
#     while not successful_query:

#         # Send the request to the OpenAI API
#         response = prompt('table', request.session.get('csv_data'))
#         if response.status_code == 200:
#             response_data = response.json()
#             result = response_data.get("choices")[0].get("message").get("content")
#             # Parse the response data into an array of objects where each object is one row in the table
#             entries = []
#             for line in result.strip().split("\n"):
#                 parts = line.split(',')
#                 # Create a dictionary for each line and append to entries
#                 try:
#                     entry = {
#                         'KeyPhrases': parts[0].strip(),
#                         'Sentiment': parts[1].strip(),
#                         'ReactionEmotion': parts[2].strip(),
#                         'ConfidenceScore': parts[3].strip(),
#                     }
#                     entries.append(entry)
#                 except:
#                     break

#             # Test data to see if resembles our expectations  
#             # Test confidence scores ensures that the value associated with the confidence score attribute is an integer between 0 and 100
#             # Test sentiment ensures that the value associated with the sentiment attribute is one of ['Positive', 'Neutral', 'Negative'] 
#             # Should either of these tests fail, the prompt is rerun after a short delay    
#             if not(test_confidence(entries) or test_sentiment(entries)):
#                 time.sleep(5)
#                 continue
#             else:
#                 print(entries)
#                 successful_query = True
            
#             request.session['table_data'] = entries
#         else:
#             return JsonResponse({'error': response.text}, status=response.status_code)
        
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

# def generate_analysis(request):
#     # Generate and execute the prompt to create the summary and table
#     summary_prompt(request)
#     table_prompt(request)

#     #calculate confidence scores 
#     confidence_frequencies = calculate_frequencies(request.session.get('table_data'))
#     request.session['confidence_frequencies'] = confidence_frequencies
    

#     return redirect('home')

def generate_analysis(csv_data):
    # Generate and execute the prompt to create the summary and table
    summary_data = summary_prompt(csv_data)
    table_data = table_prompt(csv_data)

    #calculate confidence scores 
    confidence_frequencies = calculate_frequencies(table_data)
    sentiment_frequencies = calculate_sentiment_frequencies(table_data)

    return Response({"summary": summary_data, "entries": table_data, "confidence_frequencies": confidence_frequencies, "sentiment_frequencies": sentiment_frequencies}, status=200)


@csrf_exempt  
def send_csv_to_api(request): 
    if request.method == 'POST' and 'csv_file' in request.FILES:
        # Obtain csv file passed by user
        csv_file = request.FILES['csv_file']
        # Parse the file and remove unreadable characters
        csv_data = remove_non_printable_chars(csv_file.read().decode('utf-8-sig'))
        # Add the data to the session
        request.session['csv_data'] = csv_data
        return generate_analysis(request)
        
    else:       
        return JsonResponse({'error': 'Invalid request'}, status=400)

def download_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv  ; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data_{}.csv"'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
   # response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['KeyPhrases', 'Sentiment', 'ConfidenceScore', 'ReactionEmotion'])

    entries = request.session.get('table_data',None)
    if entries:  # Check if entries is not None or empty
        for entry in entries:
            writer.writerow([
                entry.get('KeyPhrases', ''),
                entry.get('Sentiment', ''),
                entry.get('ConfidenceScore', ''),
                entry.get('ReactionEmotion', '')
            ])
    else:
        # Handle the case where there are no entries, perhaps write a row that indicates no data
        writer.writerow(['No data available.'])
    
    return response

def home(request):
    # Fetch actual data from the API or other sources here
    
    summary = request.session.get('summary', None)
    table_data = request.session.get('table_data', None)
    confidence_frequencies = request.session.get('confidence_frequencies', None)
    # sentiment_frequencies = request.session.get('sentiment_frequencies', None)

    if table_data:
        sentiment_frequencies = calculate_sentiment_frequencies(request.session.get('table_data'))
        request.session['sentiment_frequencies'] = sentiment_frequencies
    else:
        sentiment_frequencies = None

    return render(request, 'report.html', {
        'entries': table_data,
        'summary': summary,
        'confidence_frequencies': confidence_frequencies,
        'sentiment_frequencies': sentiment_frequencies
    })


