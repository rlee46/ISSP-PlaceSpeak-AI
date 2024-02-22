# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
from random import choice, randint
from datetime import datetime,timedelta
import requests
import csv
import re
import json

def remove_non_printable_chars(text):
    # Define the pattern to match only printable characters
    printable_pattern = re.compile(r'[^\x20-\x7E]')
    # Substitute non-printable characters with an empty string
    clean_text = re.sub(printable_pattern, '', text)
    return clean_text

@csrf_exempt  # Temporarily disable CSRF for this view to simplify the example
def send_csv_to_api(request):
    standard_query = """"Generate the result in csv format without any explaination. For each response,
                    column 1:Report id
                    column 2:Give me key words
                    column 3:Generate a sentimental analysis of the response from positive, neutral, or negative
                    column 4:Generate a confidence score in a percentage
                    column 5:Determine the reaction/emotion
                    Format the data as "ID, Key Words, Sentiment, Confidence Score, Reaction/Emotion
                    """
    if request.method == 'POST' and 'text_file' in request.FILES:
        text_file = request.FILES['text_file']
        text_data = remove_non_printable_chars(text_file.read().decode('utf-8-sig'))
        #print("Size of csv_data in characters:", len(text_file))
        # Combine CSV data with the standard query
        combined_data = "{}\n{}".format(standard_query, text_data)

        # Prepare data to send to the OpenAI API
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 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",  # Replace with your actual API key
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_data}
            ],
            "max_tokens": 4096,
        }

        # Send the request to the OpenAI API
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
        
            result = response_data.get("choices")[0].get("message").get("content")
        
            #print(result)
            # Parse the JSON string
            # result = json_str
            entries = []
            for line in result.strip().split("\n"):
                parts = line.split(',')
                # Create a dictionary for each line and append to entries
                entry = {
                    'ID': parts[0].strip(),
                    'KeyPhrases': parts[1].strip(),
                    'Sentiment': parts[2].strip(),
                    'ConfidenceScore': parts[3].strip(),
                    'ReactionEmotion': parts[4].strip(),
                }
                entries.append(entry)
            print(entries)
            request.session['api_response'] = entries
            return redirect('home')
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

    return JsonResponse({'error': 'Invalid request'}, status=400)

    #return JsonResponse({'error': 'Invalid request'}, status=400)
    #     if response.status_code == 200:
    #         response_data = response.json()

    #         result = response_data.get("choices")[0].get("message").get("content")
    #         start = result.find('```json') + 7  # Adjust to find the start of the JSON
    #         end = result.rfind('```')  # Find the end of the JSON
    #         json_str = result[start:end]

    #         # Parse the JSON string
    #         result = json.loads(json_str)
    #         # Return the result as a JSON response
    #         return JsonResponse({'result': result})
    #     else:
    #         return JsonResponse({'error': response.text}, status=response.status_code)

    # return JsonResponse({'error': 'Invalid request'}, status=400)
        
    
def download_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    print("Download data view was called")
    response = HttpResponse(content_type='text/csv  ; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data_{}.csv"'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
   # response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID','Key Phrases', 'Sentiment', 'Confidence Score', 'Emotion Detection'])

    entries = json.load(request.session.get('api_response',None))
    for entry in entries:
        writer.writerow([entry['id'], entry['key_phrases'], entry['sentiment'], entry['confidence_score'], entry['emotion_detection']])

    return response

def home(request):
    # Fetch actual data from the API or other sources here
    api_response = request.session.get('api_response', None)
    # print(api_response)
    if api_response:
        entries = api_response
        # Convert the string response to JSON
        del request.session['api_response']
    else:
        entries = None
    request.session.clear()
    return render(request, 'report.html', {'entries': entries})

