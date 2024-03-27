# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
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
    standard_query = """"Generate the result in csv format without any explaination. Do not include a header for the data. For each response,
                    column 1:Select one key word from the response
                    column 2:Evaluate the sentiment of the response from positive, neutral, or negative
                    column 3:Determine the reaction/emotion
                    column 4:Generate a confidence score in a percentage  
                    Format the data as Key Words, Sentiment, Reaction/Emotion, Confidence Score
                    Here is an example: `Freedom, Positive, Happy, 100%`
                    """
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']
        csv_data = remove_non_printable_chars(csv_file.read().decode('utf-8-sig'))
        #print("Size of csv_data in characters:", len(csv_file))
        # Combine CSV data with the standard query
        combined_data = "{}\n{}".format(standard_query, csv_data)

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

        successful_query = False
        while not successful_query:

        # Send the request to the OpenAI API
            response = requests.post(api_url, headers=headers, json=data)
        

            if response.status_code == 200:
                response_data = response.json()
            
                result = response_data.get("choices")[0].get("message").get("content")
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



                if not(test_confidence_scores(entries) or test_sentiment(entries)):
                    print('bad return')
                    continue
                else:
                    successful_query = True
                
                summary_query = '''I am a government  official who is looking to make a decision based on the input of my community. 
                The following data is sourced from a discussion post where members of my community discussed their views on the topic.
                Please generate a 5 to 10 sentence summary that I can use to communicate their feelings to my colleagues and other policy makers.
                In three sentences or less, please provide a recommendation for how I should proceed based on the feedback observed in this post.   
                Do not format it in markdown, only use plain text.
                ''' + csv_data
                summary_data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": summary_query}
                ],
                "max_tokens": 4096,
                }
                summary = requests.post(api_url,headers=headers, json=summary_data)
                if summary.status_code == 200:
                    summary_data = summary.json()
                    summary_result = summary_data.get("choices")[0].get("message").get("content")
                    #print(summary_result)
                else:
                    return JsonResponse({'error': response.text}, status=response.status_code)



                request.session['api_response'] = [entries, summary_result]
                return redirect('home')
            else:
                return JsonResponse({'error': response.text}, status=response.status_code)

    return JsonResponse({'error': 'Invalid request'}, status=400)
    
def download_data(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv  ; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data_{}.csv"'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
   # response['Content-Disposition'] = 'attachment; filename="sentiment_analysis_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['KeyPhrases', 'Sentiment', 'ConfidenceScore', 'ReactionEmotion'])

    entries = request.session.get('api_response',None)
    if entries:  # Check if entries is not None or empty
        for entry in entries:
            writer.writerow([
                entry.get('KeyPhrases', ''),
                entry.get('Sentiment', ''),
                entry.get('ConfidenceScore', ''),
                entry.get('ReactionEmotion', '')
            ])
        del request.session['api_response']
    else:
        # Handle the case where there are no entries, perhaps write a row that indicates no data
        writer.writerow(['No data available.'])
    
    return response

def home(request):
    # Fetch actual data from the API or other sources here
    api_response = request.session.get('api_response', None)
    if api_response:
        entries = api_response[0]
        summary = api_response[1]
        # Convert the string response to JSON
        #del request.session['api_response']
    else:
        entries = None
        summary = None
    return render(request, 'report.html', {'entries': entries, 'summary':summary})

def test_confidence_scores(data):
    for entry in data:
        try:
            a = int((entry['ConfidenceScore'].replace('%', '')))
        except:
            print('type error')
            return False
        
        if not(a >=0 or a <= 100):
            print('bad value')
            return False
        
    return True
        

def test_sentiment(data):
    sentiments = ['positive', 'neutral', 'negative']
    for entry in data:
        if not str(entry['Sentiment']).lower() in sentiments:
            print('sent')
            return False
        
    return True