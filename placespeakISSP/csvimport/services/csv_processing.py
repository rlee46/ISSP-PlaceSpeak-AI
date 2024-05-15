from django.http import JsonResponse
import os
import json
import requests
import math
import time
import csv
from collections import defaultdict
from rest_framework.response import Response

from ..utilities.helpers import HelperFunctions
from ..tests.test_functions import TestFunctions
from ..serializer import AnalysisDataSerializer

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer {api_key}".format(api_key=self.api_key),
            "Content-Type": "application/json"
        }
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")

    def generate_completion(self, query):
        query_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            "max_tokens": 4096
        }
        response = requests.post(self.api_url, headers=self.headers, json=query_data)
        return response

class DataProcessorFactory:
    def __init__(self):
        self.helper = HelperFunctions()
        self.openai_client = OpenAIClient()
        self.test = TestFunctions()

    def get_processor(self, data_type):
        if data_type == "discussion":
            return DiscussionDataProcessor(self.openai_client, self.helper, self.test)
        elif data_type == "survey":
            return SurveyDataProcessor(self.openai_client, self.helper, self.test)
        else:
            raise ValueError("Unsupported data type: {data_type}")

class DiscussionDataProcessor:
    def __init__(self, openai_client, helper, tester):
        self.openai_client = openai_client
        self.helper = helper
        self.tester = tester

    def process_batch(self, batch_data):
        resultCount = 0
        result = ""
        batch_data_str = str(batch_data)
        row_count = len(batch_data)
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
            result =  self.openai_client.generate_completion(query).json().get("choices")[0].get("message").get("content")
            resultCount = self.helper.count_csv_rows(result)
            if resultCount !=row_count: 
                    print("RERUNNING: Incorrect number of ROWS")
        
        return result

    def generate_analysis(self, csv_data):
        summary_data = self.summary_prompt(csv_data)
        table_data = self.table_prompt(csv_data)

        confidence_frequencies = self.calculate_frequencies(table_data)
        sentiment_frequencies = self.calculate_sentiment_frequencies(table_data)

        analysis_data = {
            "summary": summary_data,
            "entries": table_data,
            "confidence_frequencies": confidence_frequencies,
            "sentiment_frequencies": sentiment_frequencies
        }

        serializer = AnalysisDataSerializer(data=analysis_data)
        if serializer.is_valid():
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)
    
    def calculate_sentiment_frequencies(self,entries):
        sentiment_counts = defaultdict(int)
        for entry in entries:
            sentiment = entry.get('Sentiment', '').capitalize()
            if sentiment in ['Neutral', 'Positive', 'Negative']:
                sentiment_counts[sentiment] += 1
        return dict(sentiment_counts)

    def calculate_frequencies(self, entries):
        # Convert confidence scores to integers and bin them
        bins = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']
        score_bins = {bin: 0 for bin in bins}
    
        for entry in entries:
            score = int(entry['ConfidenceScore'].rstrip('%'))
            bin_index = min(score // 10, 9)  # to put 100% in the '90-100' bin
            bin_label = bins[bin_index]
            score_bins[bin_label] += 1

        return [score_bins[bin] for bin in bins]
    
    def prompt(self, query_type, data):
    
        # Prepare data to send to the OpenAI API
        if query_type == 'summary':
            query = '''
            I am a government  official who is looking to make a decision based on the input of my community. 
            The following data is sourced from a discussion post where members of my community discussed their views on the topic.
            Please generate a 5 to 10 sentence summary that I can use to communicate their feelings to my colleagues and other policy makers.
            In three sentences or less, please provide a recommendation for how I should proceed based on the feedback observed in this post.   
            Do not format it in markdown, only use plain text.
            ''' + data
        
            return self.openai_client.generate_completion(query)
        elif query_type == 'table':
            count = 0
            batch_size = 5
        
            data_array = self.helper.csv_to_array(data)
        
            num_rows = len(data_array)
            num_batches = math.ceil(num_rows / batch_size)
            print("number of batches: " + str(num_batches))
        
            results = []
            for i in range(int(num_batches+1)):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, num_rows)
                batch_data = data_array[start_idx:end_idx]
                if(len(batch_data) == 0):
                    break
                print("----------------------------")
                print("Batch Number: "+ str(i))
                batch_result = self.process_batch(batch_data)
                print(batch_result)
                row_result = self.helper.count_csv_rows(batch_result)
                print("result row:", row_result)
                print("----------------------------")
                count += row_result
                results.append(batch_result)
    
        print("Total Lines: " + str(count))
        return results

    def summary_prompt(self, csv_data):
        response = self.prompt('summary', csv_data)
        if response.status_code == 200:
            summary_data = response.json()
            return summary_data.get("choices")[0].get("message").get("content")
        else:
            return JsonResponse({'error': response.text}, status=response.status_code)

    def table_prompt(self, csv_data):
        # Loops the prompt untill the returned values pass the data tests
        successful_query = False
        while not successful_query:
            entries = []
            result = self.prompt('table', csv_data)
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
            if not(self.tester.test_confidence(entries) or self.tester.test_sentiment(entries)):
                time.sleep(5)
                continue
            else:
                print(entries)
                print("table_prompt done")
                successful_query = True
            
        return entries

    def build_summary_prompt(self, data):
        return """
        I am a government official making a decision based on community input.
        Here is discussion post data about members' views.
        Provide a summary in 5-10 sentences and a 3-sentence recommendation.
        {data}
        """
    
#Survey Processing
class SurveyDataProcessor:
    def __init__(self, openai_client, helper, tester):
        self.openai_client = openai_client
        self.helper = helper
        self.tester = tester

    def separate_columns(self, csv_data):
        csv_string = csv_data.encode('utf-8')
        print(csv_string)
        csv_string = csv_data['csv_data']
        csv_reader = csv.DictReader(csv_string.splitlines())
        fieldnames = csv_reader.fieldnames
        if fieldnames is None:
            raise ValueError("Fieldnames could not be extracted from CSV data.")

        # Determine columns to keep (from 8 to the second last column)
        columns_to_keep = fieldnames[7:-1]

        # Initialize a dictionary to store the JSON object
        json_object = {col: [] for col in columns_to_keep}

        # Process each row in the CSV
        for row in csv_reader:
            for col in columns_to_keep:
                json_object[col].append(row[col])

        return json.dumps(json_object, indent=2)

    